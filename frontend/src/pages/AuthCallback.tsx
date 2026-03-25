import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../stores/auth";
import type { AuthState } from "../stores/auth";

export default function AuthCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const loadUser = useAuth((s: AuthState) => s.loadUser);
  const [error, setError] = useState<string>("");

  const token = useMemo(() => params.get("token"), [params]);

  useEffect(() => {
    const run = async () => {
      if (!token) {
        setError("Missing token");
        return;
      }
      try {
        api.setToken(token);
        await loadUser();
        navigate("/", { replace: true });
      } catch (e: any) {
        api.setToken(null);
        setError(e?.message || "OAuth login failed");
      }
    };
    run();
  }, [token, loadUser, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="text-gray-700 font-medium">Signing you in...</div>
        {error && <div className="mt-2 text-sm text-red-600">{error}</div>}
      </div>
    </div>
  );
}
