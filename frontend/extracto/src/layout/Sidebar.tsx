import { NavLink } from "react-router-dom";

const items = [
  { label: "Dashboard", path: "/" },
  { label: "Projects", path: "/projects" },
  { label: "Workflows", path: "/workflows" },
  { label: "Settings", path: "/settings" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-white/10 bg-black/40 backdrop-blur-xl">
      <div className="p-6 border-b border-white/10">
        <h1 className="text-xl font-semibold tracking-wide">Extracto</h1>
        <p className="text-xs text-gray-400 mt-1">
          Intelligent Document Processing
        </p>
      </div>

      <nav className="p-4 space-y-1">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end
            className={({ isActive }) =>
              `block px-4 py-2 rounded text-sm transition ${
                isActive
                  ? "bg-white/15 text-white"
                  : "text-gray-400 hover:bg-white/10"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
