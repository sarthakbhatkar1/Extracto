import { useState } from "react";
import { api } from "../api/axios";
import { useAuth } from "./AuthContext";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    try {
      setLoading(true);

      const res = await api.post(
        "/api/v1/auth/login",
        new URLSearchParams({ username, password }),
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        }
      );

      login(res.data);
      toast.success("Login successful");

      // ✅ THIS IS THE MISSING PART
      navigate("/", { replace: true });
    } catch (err) {
      toast.error("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="glass p-8 w-96 space-y-4">
        <h1 className="text-2xl font-semibold text-center">Extracto Login</h1>

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

        <button
          onClick={handleLogin}
          disabled={loading}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="text-xs text-gray-400 text-center">
          Dummy users: <br />
          <b>user / password</b> <br />
          <b>admin / password</b>
        </p>
      </div>
    </div>
  );
}
