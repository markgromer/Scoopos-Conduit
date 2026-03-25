import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Conversations() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [convos, setConvos] = useState<any[]>([]);
  const [activeConvo, setActiveConvo] = useState<any>(null);

  useEffect(() => {
    api.listAgents().then((data) => {
      setAgents(data);
      if (data.length > 0) setSelectedAgent(data[0].id);
    });
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      api.listConversations(selectedAgent).then(setConvos);
    }
  }, [selectedAgent]);

  const openConvo = async (id: string) => {
    const detail = await api.getConversation(id);
    setActiveConvo(detail);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Conversations</h1>

      <div className="mb-6">
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
      </div>

      <div className="flex gap-6">
        {/* Conversation list */}
        <div className="w-80 bg-white rounded-xl border border-gray-200 overflow-hidden flex-shrink-0">
          <div className="divide-y divide-gray-100">
            {convos.map((c) => (
              <button
                key={c.id}
                onClick={() => openConvo(c.id)}
                className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                  activeConvo?.id === c.id ? "bg-blue-50" : ""
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    {c.channel}
                  </span>
                  <span className="text-xs text-gray-400">
                    {c.status}
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(c.updated_at).toLocaleString()}
                </p>
              </button>
            ))}
            {convos.length === 0 && (
              <p className="p-4 text-sm text-gray-400 text-center">
                No conversations yet
              </p>
            )}
          </div>
        </div>

        {/* Message thread */}
        <div className="flex-1 bg-white rounded-xl border border-gray-200 p-6">
          {activeConvo ? (
            <div>
              <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
                <div>
                  <span className="text-sm font-medium">
                    {activeConvo.channel} conversation
                  </span>
                  <span className="text-xs text-gray-400 ml-4">
                    Status: {activeConvo.status}
                  </span>
                </div>
              </div>
              <div className="space-y-3 max-h-[60vh] overflow-y-auto">
                {activeConvo.messages?.map((msg: any) => (
                  <div
                    key={msg.id}
                    className={`flex ${
                      msg.role === "agent" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[70%] px-4 py-2 rounded-xl text-sm ${
                        msg.role === "agent"
                          ? "bg-brand-600 text-white"
                          : msg.role === "lead"
                          ? "bg-gray-100 text-gray-800"
                          : "bg-yellow-50 text-yellow-800 italic"
                      }`}
                    >
                      <p>{msg.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          msg.role === "agent"
                            ? "text-blue-200"
                            : "text-gray-400"
                        }`}
                      >
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64 text-gray-400">
              Select a conversation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
