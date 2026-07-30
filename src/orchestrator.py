"""Dependency-aware stage runner inspired by modular research/execution engines."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping

from contracts import GateDecision, Status

StageFn = Callable[[Mapping[str, GateDecision]], GateDecision]

@dataclass(frozen=True)
class Stage:
    name: str
    dependencies: tuple[str, ...]
    run: StageFn

class Pipeline:
    def __init__(self, stages: Iterable[Stage]):
        rows = list(stages)
        self.stages = {stage.name: stage for stage in rows}
        if len(self.stages) != len(rows):
            raise ValueError("duplicate stage name")
        missing = {dep for stage in rows for dep in stage.dependencies if dep not in self.stages}
        if missing:
            raise ValueError(f"missing dependencies: {sorted(missing)}")
        self.order = self._topological_order()

    def _topological_order(self) -> tuple[str, ...]:
        visiting: set[str] = set()
        visited: set[str] = set()
        result: list[str] = []

        def visit(name: str) -> None:
            if name in visiting:
                raise ValueError("pipeline contains a dependency cycle")
            if name in visited:
                return
            visiting.add(name)
            for dependency in self.stages[name].dependencies:
                visit(dependency)
            visiting.remove(name)
            visited.add(name)
            result.append(name)

        for name in self.stages:
            visit(name)
        return tuple(result)

    def execute(self) -> dict[str, GateDecision]:
        decisions: dict[str, GateDecision] = {}
        for name in self.order:
            stage = self.stages[name]
            upstream = {dep: decisions[dep] for dep in stage.dependencies}
            failed = [dep for dep, result in upstream.items() if result.status is not Status.PASS]
            if failed:
                decisions[name] = GateDecision(name, Status.BLOCKED, f"upstream gates did not pass: {', '.join(failed)}")
                continue
            try:
                decision = stage.run(upstream)
                if decision.gate != name:
                    decisions[name] = GateDecision(name, Status.REJECTED, "stage returned a decision for the wrong gate")
                else:
                    decisions[name] = decision
            except Exception as exc:
                decisions[name] = GateDecision(name, Status.BLOCKED, f"stage error: {type(exc).__name__}")
        return decisions


def promotion_decision(results: Mapping[str, GateDecision], mandatory: Iterable[str]) -> GateDecision:
    required = tuple(mandatory)
    missing = [name for name in required if name not in results]
    failed = [name for name in required if name in results and results[name].status is not Status.PASS]
    if missing or failed:
        reason = f"missing={missing}; failed={failed}"
        return GateDecision("promotion", Status.REJECTED, reason)
    evidence = tuple(item for name in required for item in results[name].evidence)
    return GateDecision("promotion", Status.PASS, "all mandatory gates passed", evidence)
