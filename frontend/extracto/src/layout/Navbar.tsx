import { useAuth } from "../auth/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-white/10 bg-black/30 backdrop-blur-xl">
      <div className="text-sm text-gray-400">Workspace</div>

      <div className="flex items-center gap-4">
        <div className="text-sm">
          {user?.firstName} {user?.lastName}
        </div>

        <button
          onClick={logout}
          // className="btn btn-danger text-xs  text-red-400 hover:text-red-500"
          className="btn-secondary text-xs  text-red-400 hover:text-red-500"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
