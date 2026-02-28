export default function SettingsPage() {
  return (
    <main>
      <h2>Admin / Settings</h2>
      <div className="card">
        <p>Configure scoring weights/decay/expiry via environment variables and admin APIs.</p>
        <p>RBAC: send header <code>x-role: ADMIN</code> for admin-only operations.</p>
      </div>
    </main>
  );
}
