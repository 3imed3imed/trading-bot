"""Small cloud-neutral Experiment -> Run recorder modeled after Qlib's hierarchy."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

@dataclass(frozen=True)
class RunRecord:
    experiment_id: str
    run_id: str
    parent_run_id: str | None
    created_at: str
    code_commit: str
    data_hashes: tuple[str, ...]
    policy_hash: str
    parameters: Mapping[str, Any]
    metrics: Mapping[str, float | int | None]
    artifacts: tuple[str, ...]
    mode: str

    @property
    def fingerprint(self) -> str:
        canonical = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()


def create_run(*, experiment_id: str, run_id: str, code_commit: str, data_hashes: tuple[str, ...], policy_hash: str, parameters: Mapping[str, Any], metrics: Mapping[str, float | int | None], artifacts: tuple[str, ...], mode: str, parent_run_id: str | None = None) -> RunRecord:
    if not experiment_id or not run_id or not code_commit or not policy_hash:
        raise ValueError("experiment, run, commit and policy identifiers are mandatory")
    if not data_hashes:
        raise ValueError("at least one immutable data hash is mandatory")
    return RunRecord(
        experiment_id=experiment_id,
        run_id=run_id,
        parent_run_id=parent_run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        code_commit=code_commit,
        data_hashes=data_hashes,
        policy_hash=policy_hash,
        parameters=dict(parameters),
        metrics=dict(metrics),
        artifacts=artifacts,
        mode=mode,
    )
