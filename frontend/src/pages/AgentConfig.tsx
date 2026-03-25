import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";

export default function AgentConfig() {
  const { agentId } = useParams<{ agentId: string }>();
  const [agent, setAgent] = useState<any>(null);
  const [tab, setTab] = useState<string>("voice");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (agentId) api.getAgent(agentId).then(setAgent);
  }, [agentId]);

  if (!agent) return <div className="text-gray-500">Loading...</div>;

  const save = async (updates: Record<string, any>) => {
    setSaving(true);
    const updated = await api.updateAgent(agent.id, updates);
    setAgent(updated);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const tabs = [
    { id: "voice", label: "Brand Voice" },
    { id: "pricing", label: "Pricing" },
    { id: "areas", label: "Service Areas" },
    { id: "objections", label: "Objections" },
    { id: "channels", label: "Channels" },
    { id: "crm", label: "CRM" },
    { id: "advanced", label: "Advanced" },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{agent.name}</h1>
          <p className="text-gray-500">
            {agent.business_name} - {agent.business_type}
          </p>
        </div>
        {saved && (
          <span className="text-sm text-green-600 font-medium">Saved</span>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <div className="flex gap-6">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                tab === t.id
                  ? "border-brand-600 text-brand-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab content */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        {tab === "voice" && <VoiceTab agent={agent} onSave={save} saving={saving} />}
        {tab === "pricing" && <PricingTab agent={agent} onRefresh={() => api.getAgent(agent.id).then(setAgent)} />}
        {tab === "areas" && <ServiceAreaTab agent={agent} onRefresh={() => api.getAgent(agent.id).then(setAgent)} />}
        {tab === "objections" && <ObjectionsTab agent={agent} onRefresh={() => api.getAgent(agent.id).then(setAgent)} />}
        {tab === "channels" && <ChannelsTab agent={agent} onSave={save} saving={saving} />}
        {tab === "crm" && <CrmTab agent={agent} onSave={save} saving={saving} />}
        {tab === "advanced" && <AdvancedTab agent={agent} onSave={save} saving={saving} />}
      </div>
    </div>
  );
}

/* ── Voice tab ── */
function VoiceTab({ agent, onSave, saving }: any) {
  const [brandVoice, setBrandVoice] = useState(agent.brand_voice || "");
  const [greeting, setGreeting] = useState(agent.greeting_message || "");
  const [fallback, setFallback] = useState(agent.fallback_message || "");

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Brand Voice & Tone
        </label>
        <p className="text-xs text-gray-400 mb-2">
          Describe how the agent should communicate. Example: "Friendly and
          casual, use first names, avoid jargon, keep responses under 3
          sentences."
        </p>
        <textarea
          value={brandVoice}
          onChange={(e) => setBrandVoice(e.target.value)}
          rows={5}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Greeting Message
        </label>
        <p className="text-xs text-gray-400 mb-2">
          First message the AI sends to new leads.
        </p>
        <textarea
          value={greeting}
          onChange={(e) => setGreeting(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Fallback Message
        </label>
        <input
          value={fallback}
          onChange={(e) => setFallback(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <button
        onClick={() =>
          onSave({
            brand_voice: brandVoice,
            greeting_message: greeting,
            fallback_message: fallback,
          })
        }
        disabled={saving}
        className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save Changes"}
      </button>
    </div>
  );
}

/* ── Pricing tab ── */
function PricingTab({ agent, onRefresh }: any) {
  const [name, setName] = useState("");
  const [min, setMin] = useState("");
  const [max, setMax] = useState("");
  const [unit, setUnit] = useState("per job");
  const [isSub, setIsSub] = useState(false);
  const [desc, setDesc] = useState("");

  const add = async () => {
    if (!name || !min) return;
    await api.addPricing(agent.id, {
      service_name: name,
      description: desc,
      price_min: parseFloat(min),
      price_max: max ? parseFloat(max) : null,
      price_unit: unit,
      is_subscription: isSub,
    });
    setName("");
    setMin("");
    setMax("");
    setDesc("");
    onRefresh();
  };

  const remove = async (id: string) => {
    await api.removePricing(agent.id, id);
    onRefresh();
  };

  return (
    <div>
      <h3 className="font-medium mb-4">Service Pricing</h3>
      {agent.pricing?.length > 0 && (
        <div className="mb-6 space-y-2">
          {agent.pricing.map((p: any) => (
            <div
              key={p.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <span className="font-medium text-sm">{p.service_name}</span>
                <span className="text-sm text-gray-500 ml-2">
                  ${p.price_min}
                  {p.price_max ? ` - $${p.price_max}` : ""} {p.price_unit}
                </span>
                {p.is_subscription && (
                  <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                    subscription
                  </span>
                )}
              </div>
              <button
                onClick={() => remove(p.id)}
                className="text-red-500 text-sm hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <input
          placeholder="Service name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="Description (optional)"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="Min price"
          type="number"
          value={min}
          onChange={(e) => setMin(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="Max price (optional)"
          type="number"
          value={max}
          onChange={(e) => setMax(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <select
          value={unit}
          onChange={(e) => setUnit(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
        >
          <option value="per job">Per Job</option>
          <option value="per hour">Per Hour</option>
          <option value="per sqft">Per Sq Ft</option>
          <option value="monthly">Monthly</option>
          <option value="per visit">Per Visit</option>
        </select>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={isSub}
            onChange={(e) => setIsSub(e.target.checked)}
          />
          Subscription service
        </label>
      </div>
      <button
        onClick={add}
        className="mt-4 px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
      >
        Add Pricing
      </button>
    </div>
  );
}

/* ── Service Area tab ── */
function ServiceAreaTab({ agent, onRefresh }: any) {
  const [zip, setZip] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [radius, setRadius] = useState("");

  const add = async () => {
    if (!zip && !city) return;
    await api.addServiceArea(agent.id, {
      zip_code: zip,
      city,
      state,
      radius_miles: radius ? parseFloat(radius) : 0,
    });
    setZip("");
    setCity("");
    setState("");
    setRadius("");
    onRefresh();
  };

  const remove = async (id: string) => {
    await api.removeServiceArea(agent.id, id);
    onRefresh();
  };

  return (
    <div>
      <h3 className="font-medium mb-4">Service Areas</h3>
      {agent.service_areas?.length > 0 && (
        <div className="mb-6 space-y-2">
          {agent.service_areas.map((a: any) => (
            <div
              key={a.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <span className="text-sm">
                {a.city} {a.state} {a.zip_code}
                {a.radius_miles ? ` (+${a.radius_miles} mi)` : ""}
              </span>
              <button
                onClick={() => remove(a.id)}
                className="text-red-500 text-sm hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <input
          placeholder="ZIP code"
          value={zip}
          onChange={(e) => setZip(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="City"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="State"
          value={state}
          onChange={(e) => setState(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <input
          placeholder="Radius (miles)"
          type="number"
          value={radius}
          onChange={(e) => setRadius(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <button
        onClick={add}
        className="mt-4 px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
      >
        Add Area
      </button>
    </div>
  );
}

/* ── Objections tab ── */
function ObjectionsTab({ agent, onRefresh }: any) {
  const [trigger, setTrigger] = useState("");
  const [script, setScript] = useState("");

  const add = async () => {
    if (!trigger || !script) return;
    await api.addObjection(agent.id, {
      objection_trigger: trigger,
      response_script: script,
    });
    setTrigger("");
    setScript("");
    onRefresh();
  };

  const remove = async (id: string) => {
    await api.removeObjection(agent.id, id);
    onRefresh();
  };

  return (
    <div>
      <h3 className="font-medium mb-2">Objection Handling</h3>
      <p className="text-xs text-gray-400 mb-4">
        Teach the agent how to respond when leads push back. Enter the objection
        (what they say) and the script (how to respond).
      </p>

      {agent.objections?.length > 0 && (
        <div className="mb-6 space-y-2">
          {agent.objections.map((o: any) => (
            <div key={o.id} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-sm font-medium text-red-600">
                    "{o.objection_trigger}"
                  </span>
                  <p className="text-sm text-gray-600 mt-1">
                    {o.response_script}
                  </p>
                </div>
                <button
                  onClick={() => remove(o.id)}
                  className="text-red-500 text-sm hover:text-red-700"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="space-y-3">
        <input
          placeholder='Objection (e.g., "too expensive")'
          value={trigger}
          onChange={(e) => setTrigger(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
        <textarea
          placeholder="Response script"
          value={script}
          onChange={(e) => setScript(e.target.value)}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <button
        onClick={add}
        className="mt-4 px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
      >
        Add Objection Handler
      </button>
    </div>
  );
}

/* ── Channels tab ── */
function ChannelsTab({ agent, onSave, saving }: any) {
  const [phone, setPhone] = useState(agent.twilio_phone_number || "");
  const [pageId, setPageId] = useState(agent.meta_page_id || "");
  const [igId, setIgId] = useState(agent.meta_ig_account_id || "");
  const [emailInbox, setEmailInbox] = useState(agent.email_inbox || "");

  return (
    <div className="space-y-5">
      <h3 className="font-medium">Channel Connections</h3>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          SMS (Twilio Phone Number)
        </label>
        <input
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="+1234567890"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Facebook Page ID
        </label>
        <input
          value={pageId}
          onChange={(e) => setPageId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Instagram Account ID
        </label>
        <input
          value={igId}
          onChange={(e) => setIgId(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email Inbox
        </label>
        <input
          value={emailInbox}
          onChange={(e) => setEmailInbox(e.target.value)}
          placeholder="leads@yourdomain.com"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Lead Form:</strong> Embed forms on any website using this
          webhook URL:
        </p>
        <code className="text-xs bg-white px-2 py-1 rounded mt-1 block text-blue-700">
          POST /api/webhooks/lead-form/{agent.id}
        </code>
      </div>

      <button
        onClick={() =>
          onSave({
            twilio_phone_number: phone,
            meta_page_id: pageId,
            meta_ig_account_id: igId,
            email_inbox: emailInbox,
          })
        }
        disabled={saving}
        className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save Channels"}
      </button>
    </div>
  );
}

/* ── CRM tab ── */
function CrmTab({ agent, onSave, saving }: any) {
  const [crmType, setCrmType] = useState(agent.crm_type || "ghl");
  const [apiKey, setApiKey] = useState(agent.crm_api_key || "");
  const [webhookUrl, setWebhookUrl] = useState(agent.crm_webhook_url || "");
  const [pipelineId, setPipelineId] = useState(agent.crm_pipeline_id || "");
  const [stageId, setStageId] = useState(agent.crm_stage_id || "");

  return (
    <div className="space-y-5">
      <h3 className="font-medium">CRM Integration</h3>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          CRM Type
        </label>
        <select
          value={crmType}
          onChange={(e) => setCrmType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
        >
          <option value="ghl">GoHighLevel</option>
          <option value="webhook">Generic Webhook</option>
          <option value="zapier">Zapier</option>
        </select>
      </div>

      {crmType === "ghl" && (
        <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              GHL API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Pipeline ID
            </label>
            <input
              value={pipelineId}
              onChange={(e) => setPipelineId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stage ID
            </label>
            <input
              value={stageId}
              onChange={(e) => setStageId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
        </>
      )}

      {(crmType === "webhook" || crmType === "zapier") && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Webhook URL
          </label>
          <input
            value={webhookUrl}
            onChange={(e) => setWebhookUrl(e.target.value)}
            placeholder="https://hooks.zapier.com/..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>
      )}

      <button
        onClick={() =>
          onSave({
            crm_type: crmType,
            crm_api_key: apiKey,
            crm_webhook_url: webhookUrl,
            crm_pipeline_id: pipelineId,
            crm_stage_id: stageId,
          })
        }
        disabled={saving}
        className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save CRM Settings"}
      </button>
    </div>
  );
}

/* ── Advanced tab ── */
function AdvancedTab({ agent, onSave, saving }: any) {
  const [guardrails, setGuardrails] = useState(agent.guardrails || "");
  const [maxDiscount, setMaxDiscount] = useState(
    String(agent.max_discount_percent || 0)
  );
  const [handoffKeywords, setHandoffKeywords] = useState(
    (agent.require_human_handoff_keywords || []).join(", ")
  );
  const [requiredFields, setRequiredFields] = useState(
    (agent.required_lead_fields || []).join(", ")
  );
  const [customQuestions, setCustomQuestions] = useState(
    (agent.custom_questions || []).join("\n")
  );
  const [bookingUrl, setBookingUrl] = useState(agent.booking_url || "");
  const [duration, setDuration] = useState(
    String(agent.appointment_duration_minutes || 60)
  );

  return (
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Guardrails
        </label>
        <p className="text-xs text-gray-400 mb-2">
          Things the agent should never say or do.
        </p>
        <textarea
          value={guardrails}
          onChange={(e) => setGuardrails(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Max Discount %
          </label>
          <input
            type="number"
            value={maxDiscount}
            onChange={(e) => setMaxDiscount(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Appointment Duration (min)
          </label>
          <input
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Human Handoff Keywords
        </label>
        <p className="text-xs text-gray-400 mb-2">
          Comma-separated words that trigger an instant handoff to a human.
        </p>
        <input
          value={handoffKeywords}
          onChange={(e) => setHandoffKeywords(e.target.value)}
          placeholder="manager, complaint, lawyer, sue"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Required Lead Fields
        </label>
        <input
          value={requiredFields}
          onChange={(e) => setRequiredFields(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Custom Qualifying Questions
        </label>
        <p className="text-xs text-gray-400 mb-2">One per line.</p>
        <textarea
          value={customQuestions}
          onChange={(e) => setCustomQuestions(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Booking URL
        </label>
        <input
          value={bookingUrl}
          onChange={(e) => setBookingUrl(e.target.value)}
          placeholder="https://calendly.com/..."
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
        />
      </div>

      <button
        onClick={() =>
          onSave({
            guardrails,
            max_discount_percent: parseFloat(maxDiscount) || 0,
            require_human_handoff_keywords: handoffKeywords
              .split(",")
              .map((s: string) => s.trim())
              .filter(Boolean),
            required_lead_fields: requiredFields
              .split(",")
              .map((s: string) => s.trim())
              .filter(Boolean),
            custom_questions: customQuestions
              .split("\n")
              .map((s: string) => s.trim())
              .filter(Boolean),
            booking_url: bookingUrl,
            appointment_duration_minutes: parseInt(duration) || 60,
          })
        }
        disabled={saving}
        className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save Advanced Settings"}
      </button>
    </div>
  );
}
