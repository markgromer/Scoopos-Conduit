const API_BASE = "/api";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem("conduit_token", token);
    } else {
      localStorage.removeItem("conduit_token");
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem("conduit_token");
    }
    return this.token;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const resp = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers,
    });

    if (resp.status === 401) {
      this.setToken(null);
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }

    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed: ${resp.status}`);
    }

    if (resp.status === 204) return {} as T;
    return resp.json();
  }

  // Auth
  async register(email: string, password: string, companyName: string) {
    return this.request<{ access_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, company_name: companyName }),
    });
  }

  async login(email: string, password: string) {
    return this.request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getMe() {
    return this.request<any>("/auth/me");
  }

  // Agents
  async listAgents() {
    return this.request<any[]>("/agents/");
  }

  async getAgent(id: string) {
    return this.request<any>(`/agents/${id}`);
  }

  async createAgent(data: any) {
    return this.request<any>("/agents/", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateAgent(id: string, data: any) {
    return this.request<any>(`/agents/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async startMetaConnect(agentId: string) {
    return this.request<{ url: string }>(
      `/agents/${agentId}/meta/connect/start?return_url=1`
    );
  }

  async getMetaConnectStatus(agentId: string) {
    return this.request<any>(`/agents/${agentId}/meta/connect/status`);
  }

  async getMetaConnectSession(agentId: string, sessionId: string) {
    return this.request<any>(
      `/agents/${agentId}/meta/connect/session/${sessionId}`
    );
  }

  async completeMetaConnect(agentId: string, sessionId: string, pageId: string) {
    return this.request<any>(`/agents/${agentId}/meta/connect/complete`, {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, page_id: pageId }),
    });
  }

  async disconnectMetaConnect(agentId: string) {
    return this.request<any>(`/agents/${agentId}/meta/connect`, {
      method: "DELETE",
    });
  }

  async deleteAgent(id: string) {
    return this.request<void>(`/agents/${id}`, { method: "DELETE" });
  }

  // Pricing
  async addPricing(agentId: string, data: any) {
    return this.request<any>(`/agents/${agentId}/pricing`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async removePricing(agentId: string, pricingId: string) {
    return this.request<void>(`/agents/${agentId}/pricing/${pricingId}`, {
      method: "DELETE",
    });
  }

  // Service areas
  async addServiceArea(agentId: string, data: any) {
    return this.request<any>(`/agents/${agentId}/service-areas`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async removeServiceArea(agentId: string, areaId: string) {
    return this.request<void>(`/agents/${agentId}/service-areas/${areaId}`, {
      method: "DELETE",
    });
  }

  // Objections
  async addObjection(agentId: string, data: any) {
    return this.request<any>(`/agents/${agentId}/objections`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async removeObjection(agentId: string, objectionId: string) {
    return this.request<void>(
      `/agents/${agentId}/objections/${objectionId}`,
      { method: "DELETE" }
    );
  }

  // Dashboard
  async getStats(agentId: string) {
    return this.request<any>(`/dashboard/stats?agent_id=${agentId}`);
  }

  async listLeads(agentId: string, status?: string) {
    const params = new URLSearchParams({ agent_id: agentId });
    if (status) params.set("status", status);
    return this.request<any[]>(`/dashboard/leads?${params}`);
  }

  async listConversations(agentId: string) {
    return this.request<any[]>(
      `/dashboard/conversations?agent_id=${agentId}`
    );
  }

  async getConversation(id: string) {
    return this.request<any>(`/dashboard/conversations/${id}`);
  }

  async listAppointments(agentId: string) {
    return this.request<any[]>(
      `/dashboard/appointments?agent_id=${agentId}`
    );
  }
}

export const api = new ApiClient();
