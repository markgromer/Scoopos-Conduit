import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../stores/auth";

export default function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState<"google" | "facebook" | "">("");
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const startOAuth = async (provider: "google" | "facebook") => {
    setError("");
    setOauthLoading(provider);
    try {
      const resp = await fetch(`/api/auth/oauth/${provider}/start?return_url=1`);
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `OAuth unavailable (${resp.status})`);
      }
      const body = (await resp.json()) as { url?: string };
      if (!body.url) throw new Error("OAuth start failed");
      window.location.href = body.url;
    } catch (err: any) {
      setError(err.message || "OAuth start failed");
    } finally {
      setOauthLoading("");
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, companyName);
      } else {
        await login(email, password);
      }
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Conduit</h1>
          <p className="text-gray-500 mt-2">AI-Powered Lead Agent</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-lg font-semibold mb-6">
            {isRegister ? "Create Account" : "Sign In"}
          </h2>

          <div className="space-y-3 mb-6">
            <button
              type="button"
              onClick={() => {
                startOAuth("google");
              }}
              disabled={loading || oauthLoading !== ""}
              className="w-full py-2.5 bg-white text-gray-900 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              {oauthLoading === "google" ? "..." : "Continue with Google"}
            </button>
            <button
              type="button"
              onClick={() => {
                startOAuth("facebook");
              }}
              disabled={loading || oauthLoading !== ""}
              className="w-full py-2.5 bg-white text-gray-900 font-medium rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors"
            >
              {oauthLoading === "facebook" ? "..." : "Continue with Facebook"}
            </button>
            <div className="flex items-center gap-3">
              <div className="h-px flex-1 bg-gray-200" />
              <div className="text-xs text-gray-500">or</div>
              <div className="h-px flex-1 bg-gray-200" />
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name
                </label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
                  required
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
                required
                minLength={8}
              />
            </div>

            {error && (
              <p className="text-sm text-red-600">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-brand-600 text-white font-medium rounded-lg hover:bg-brand-700 transition-colors disabled:opacity-50"
            >
              {loading
                ? "..."
                : isRegister
                ? "Create Account"
                : "Sign In"}
            </button>
          </form>

          <p className="mt-4 text-center text-sm text-gray-500">
            {isRegister ? "Already have an account?" : "Need an account?"}{" "}
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
              }}
              className="text-brand-600 font-medium hover:underline"
            >
              {isRegister ? "Sign in" : "Register"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
