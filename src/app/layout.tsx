import "./globals.css";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <h1>Signal Intelligence Hub</h1>
          <nav>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/signals">Signals Feed</Link>
            <Link href="/sources">Sources</Link>
            <Link href="/analytics">Analytics</Link>
            <Link href="/settings">Settings</Link>
            <Link href="/connector-status">Connector Status</Link>
          </nav>
          {children}
        </div>
      </body>
    </html>
  );
}
