"use client";
import useSWR from "swr";
const fetcher = (u: string) => fetch(u).then((r) => r.json());

export default function ConnectorStatusPage() {
  const { data } = useSWR("/api/connector-status", fetcher);
  return (
    <main>
      <h2>Connector Status</h2>
      <table>
        <thead><tr><th>Name</th><th>Type</th><th>Status</th><th>Notes</th></tr></thead>
        <tbody>
          {data?.map((d: any) => <tr key={d.name}><td>{d.name}</td><td>{d.sourceType}</td><td>{d.connectorStatus}</td><td>{d.connectorReason}</td></tr>)}
        </tbody>
      </table>
    </main>
  );
}
