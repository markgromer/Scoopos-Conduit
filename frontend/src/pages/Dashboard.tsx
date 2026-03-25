import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function Dashboard() {
  const [agents, setAgents] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [selectedAgent, setSelectedAgent] = useState<string>("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newBusiness, setNewBusiness] = useState("");
  const [newType, setNewType] = useState("plumbing");
  const navigate = useNavigate();

  useEffect(() => {
    api.listAgents().then((data) => {
      setAgents(data);
      if (data.length > 0) setSelectedAgent(data[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      api.getStats(selectedAgent).then(setStats);
    }
  }, [selectedAgent]);

  const handleCreate = async () => {
    if (!newName || !newBusiness) return;
    const agent = await api.createAgent({
      name: newName,
      business_name: newBusiness,
      business_type: newType,
    });
    setAgents([agent, ...agents]);
    setSelectedAgent(agent.id);
    setShowCreate(false);
    setNewName("");
    setNewBusiness("");
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Your AI agents at a glance</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700 transition-colors"
        >
          + New Agent
        </button>
      </div>

      {/* Agent selector */}
      {agents.length > 0 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Active Agent
          </label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg bg-white"
          >
            {agents.map((a) => (
              <option key={a.id} value={a.id}>
                {a.name} - {a.business_name}
              </option>
            ))}
          </select>
          {selectedAgent && (
            <Link
              to={`/agent/${selectedAgent}`}
              className="ml-4 text-sm text-brand-600 hover:underline"
            >
              Configure agent
            </Link>
          )}
        </div>
      )}

      {/* Stats cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Leads" value={stats.total_leads} />
          <StatCard label="Booked" value={stats.booked_leads} />
          <StatCard
            label="Active Conversations"
            value={stats.active_conversations}
          />
          <StatCard
            label="Conversion Rate"
            value={`${stats.conversion_rate}%`}
          />
        </div>
      )}

      {agents.length === 0 && !showCreate && (
        <div className="text-center py-20 bg-white rounded-xl border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            No agents yet
          </h3>
          <p className="text-gray-500 mt-2">
            Create your first AI agent to start converting leads.
          </p>
          <button
            onClick={() => setShowCreate(true)}
            className="mt-4 px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-medium hover:bg-brand-700"
          >
            Create Agent
          </button>
        </div>
      )}

      {/* Create agent modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold mb-4">New Agent</h2>
            <div className="space-y-3">
              <input
                placeholder="Agent name (e.g., Main SMS Bot)"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <input
                placeholder="Business name"
                value={newBusiness}
                onChange={(e) => setNewBusiness(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
              <select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white"
              >
                <option value="plumbing">Plumbing</option>
                <option value="hvac">HVAC</option>
                <option value="roofing">Roofing</option>
                <option value="cleaning">Cleaning</option>
                <option value="landscaping">Landscaping</option>
                <option value="pest_control">Pest Control</option>
                <option value="electrical">Electrical</option>
                <option value="painting">Painting</option>
                <option value="moving">Moving</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}
