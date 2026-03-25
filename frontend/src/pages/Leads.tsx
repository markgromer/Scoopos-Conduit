import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Leads() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [leads, setLeads] = useState<any[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    api.listAgents().then((data) => {
      setAgents(data);
      if (data.length > 0) setSelectedAgent(data[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      api.listLeads(selectedAgent, filter || undefined).then(setLeads);
    }
  }, [selectedAgent, filter]);

  const statusColors: Record<string, string> = {
    new: "bg-blue-100 text-blue-700",
    qualifying: "bg-yellow-100 text-yellow-700",
    quoted: "bg-purple-100 text-purple-700",
    booked: "bg-green-100 text-green-700",
    subscribed: "bg-emerald-100 text-emerald-700",
    lost: "bg-gray-100 text-gray-500",
    handed_off: "bg-orange-100 text-orange-700",
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Leads</h1>

      <div className="flex gap-4 mb-6">
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
        >
          {agents.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
        >
          <option value="">All statuses</option>
          <option value="new">New</option>
          <option value="qualifying">Qualifying</option>
          <option value="quoted">Quoted</option>
          <option value="booked">Booked</option>
          <option value="lost">Lost</option>
        </select>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Name
              </th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Contact
              </th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Service
              </th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Status
              </th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Channel
              </th>
              <th className="text-left px-4 py-3 font-medium text-gray-500">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {leads.map((lead) => (
              <tr key={lead.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">
                  {lead.name || "Unknown"}
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {lead.phone || lead.email || "-"}
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {lead.service_requested || "-"}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-medium ${
                      statusColors[lead.status] || "bg-gray-100"
                    }`}
                  >
                    {lead.status}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {lead.source_channel}
                </td>
                <td className="px-4 py-3 text-gray-400">
                  {new Date(lead.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
            {leads.length === 0 && (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-gray-400"
                >
                  No leads yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
