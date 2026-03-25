import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../stores/auth";
import clsx from "clsx";

const nav = [
  { name: "Dashboard", href: "/" },
  { name: "Leads", href: "/leads" },
  { name: "Conversations", href: "/conversations" },
  { name: "Settings", href: "/settings" },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { user, logout } = useAuth();

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold tracking-tight">Conduit</h1>
          <p className="text-xs text-gray-400 mt-1">AI Lead Agent</p>
        </div>
        <nav className="flex-1 px-4 space-y-1">
          {nav.map((item) => (
            <Link
              key={item.href}
              to={item.href}
              className={clsx(
                "block px-3 py-2 rounded-md text-sm font-medium transition-colors",
                location.pathname === item.href
                  ? "bg-gray-800 text-white"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              )}
            >
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <p className="text-sm text-gray-400 truncate">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-2 text-xs text-gray-500 hover:text-white transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-8">{children}</main>
    </div>
  );
}
