import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { api } from "../api/axios";

export default function SignupPage() {
  const navigate = useNavigate();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!firstName || !lastName || !email || !password) {
      toast.error("Please fill all fields");
      return;
    }

    try {
      setLoading(true);

      await api.post("/api/v1/auth/register", {
        email,
        password,
        firstName,
        lastName,
        role: "User",
      });

      toast.success("Account created successfully");
      navigate("/login");
    } catch {
      toast.error("Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="glass w-full max-w-md p-8 space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-2xl font-semibold">
            Create your Extracto workspace
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Start organizing and processing documents intelligently.
          </p>
        </div>

        {/* Form */}
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <input
              className="input"
              placeholder="First name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
            <input
              className="input"
              placeholder="Last name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>

          <input
            className="input"
            placeholder="Work email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
          onClick={handleSignup}
          disabled={loading}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>

        {/* Footer */}
        <p className="text-xs text-gray-400 text-center">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-400 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
