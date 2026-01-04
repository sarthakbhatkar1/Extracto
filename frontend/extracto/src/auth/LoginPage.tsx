import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { api } from "../api/axios";
import { useAuth } from "./AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      toast.error("Enter username and password");
      return;
    }

    try {
      setLoading(true);

      const res = await api.post(
        "/api/v1/auth/login",
        new URLSearchParams({
          username,
          password,
        }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      login(res.data);
      toast.success("Signed in successfully");
      navigate("/", { replace: true });
    } catch {
      toast.error("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950">
      <div className="w-full max-w-md glass p-8 space-y-6">
        {/* Header */}
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold">Sign in to Extracto</h1>
          <p className="text-sm text-slate-400">
            Access your document intelligence workspace.
          </p>
        </div>

        {/* Form */}
        <div className="space-y-4">
          <input
            className="input"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            className="input"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* CTA */}
        <button
          onClick={handleLogin}
          disabled={loading}
          className="btn-primary w-full"
        >
          {loading ? "Signing in…" : "Sign in"}
        </button>

        {/* Footer */}
        <div className="text-sm text-slate-400 text-center">
          Don’t have an account?{" "}
          <Link to="/signup" className="text-blue-400 hover:underline">
            Create one
          </Link>
        </div>
      </div>
    </div>
  );
}
