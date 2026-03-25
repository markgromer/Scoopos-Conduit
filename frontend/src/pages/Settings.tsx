import { useAuth } from "../stores/auth";

export default function Settings() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      <div className="bg-white rounded-xl border border-gray-200 p-6 max-w-2xl">
        <h2 className="text-lg font-semibold mb-4">Account</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-500">
              Email
            </label>
            <p className="text-sm text-gray-900">{user?.email}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500">
              Company
            </label>
            <p className="text-sm text-gray-900">{user?.company_name}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-500">
              Account ID
            </label>
            <p className="text-sm text-gray-400 font-mono">{user?.id}</p>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 max-w-2xl mt-6">
        <h2 className="text-lg font-semibold mb-4">API Access</h2>
        <p className="text-sm text-gray-500 mb-3">
          Use these endpoints to connect external systems:
        </p>
        <div className="space-y-2 text-sm font-mono bg-gray-50 p-4 rounded-lg">
          <p>
            <span className="text-green-600">POST</span>{" "}
            /api/webhooks/lead-form/:agent_id
          </p>
          <p>
            <span className="text-green-600">POST</span> /api/webhooks/sms
          </p>
          <p>
            <span className="text-green-600">POST</span> /api/webhooks/meta
          </p>
          <p>
            <span className="text-green-600">POST</span> /api/webhooks/email
          </p>
        </div>
      </div>
    </div>
  );
}
