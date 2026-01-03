export default function Settings() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-gray-400 text-sm">
          Manage your account and application preferences.
        </p>
      </div>

      <div className="glass p-6 space-y-4">
        <h3 className="section-title">Account</h3>

        <div className="text-sm text-gray-300">
          Profile management, password change, and security options will be
          available here.
        </div>
      </div>

      <div className="glass p-6 space-y-4">
        <h3 className="section-title">Application</h3>

        <div className="text-sm text-gray-300">
          Theme preferences, notification settings, and workspace configuration.
        </div>
      </div>
    </div>
  );
}
