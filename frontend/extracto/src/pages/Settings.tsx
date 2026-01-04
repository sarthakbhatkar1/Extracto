import { useAuth } from "../auth/AuthContext";

export default function Settings() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-slate-400">
          Manage your profile and application preferences.
        </p>
      </div>

      {/* Profile */}
      <div className="glass p-6 space-y-4">
        <h2 className="section-title">Profile</h2>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-400">First name</p>
            <p>{user.firstName}</p>
          </div>

          <div>
            <p className="text-slate-400">Last name</p>
            <p>{user.lastName}</p>
          </div>

          <div>
            <p className="text-slate-400">Username</p>
            <p>{user.username}</p>
          </div>

          <div>
            <p className="text-slate-400">Role</p>
            <p>{user.role}</p>
          </div>

          <div className="col-span-2">
            <p className="text-slate-400">Account created</p>
            <p>{new Date(user.created_at).toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="glass p-6 space-y-4">
        <h2 className="section-title">Application</h2>

        <p className="text-sm text-slate-400">
          Preferences like notifications, themes, and integrations will be
          available here.
        </p>
      </div>
    </div>
  );
}
