import {readFile} from "node:fs/promises";

// Simple Responses API tool loop. The model decides WHICH READ TOOL TO CALL,
// but the server validates every argument and gates all record writes.
export const TOOLS=[
  {type:"function",name:"list_leads",description:"Read fictional leads from the local demo datastore. Leave stage empty to list all.",strict:true,parameters:{type:"object",properties:{stage:{type:"string",description:"Stage filter, or empty string"}},required:["stage"],additionalProperties:false}},
  {type:"function",name:"get_lead",description:"Read one fictional customer lead by exact lead ID.",strict:true,parameters:{type:"object",properties:{lead_id:{type:"string",description:"Exact lead ID e.g. L-001"}},required:["lead_id"],additionalProperties:false}},
  {type:"function",name:"propose_lead_update",description:"Create a proposal for HUMAN approval. Does NOT change the record. Use empty strings for unchanged fields. Never send messages or process payments.",strict:true,parameters:{type:"object",properties:{lead_id:{type:"string"},stage:{type:"string"},next_follow_up:{type:"string"},note:{type:"string"},reason:{type:"string"}},required:["lead_id","stage","next_follow_up","note","reason"],additionalProperties:false}}
];

export class LeadAgent {
  constructor({store,key,model="gpt-4.1-mini",fetchImpl=fetch,instructionsFile}){
    this.store=store;this.key=key;this.model=model;this.fetchImpl=fetchImpl;this.instructionsFile=instructionsFile;
  }
  tool(name,args){
    if(!args||typeof args!=="object"||Array.isArray(args))return {error:"Expected object arguments"};
    if(name==="list_leads")return {status:"ok",records:this.store.list(String(args.stage||""))};
    if(name==="get_lead")return {status:"ok",record:this.store.get(String(args.lead_id||""))};
    if(name==="propose_lead_update")return this.store.propose(args);
    return {error:"Unknown tool"};
  }
  async ask(prompt){
    if(!this.key)throw Error("Missing OPENAI_API_KEY. Copy .env.example to .env and add your own server-side key.");
    if(typeof prompt!=="string"||!prompt.trim()||prompt.length>5000)throw Error("Message must be 1–5000 characters");
    const system=await readFile(this.instructionsFile,"utf8");
    const input=[{role:"user",content:prompt.trim()}], trace=[];
    for(let step=0;step<6;step++){
      const res=await this.fetchImpl("https://api.openai.com/v1/responses",{
        method:"POST",
        headers:{"Authorization":"Bearer "+this.key,"Content-Type":"application/json"},
        body:JSON.stringify({model:this.model,store:false,instructions:system,
          input,tools:TOOLS,tool_choice:"auto",max_output_tokens:1600})
      });
      let response;
      try{response=await res.json();}catch(e){throw Error("Model returned an unreadable response");}
      if(!res.ok)throw Error("Model request failed ("+res.status+"): "+String(response?.error?.message||"Check model, key and billing").slice(0,200));
      if(!Array.isArray(response.output))throw Error("Model response lacks an output list");
      const calls=response.output.filter(o=>o.type==="function_call");
      if(!calls.length){
        const text=response.output_text||response.output.filter(o=>o.type==="message").flatMap(m=>m.content||[]).filter(c=>c.type==="output_text").map(c=>c.text).join("\n");
        return {answer:text||"No text response was produced.",trace,pending:this.store.snapshot().pending};
      }
      input.push(...response.output);
      for(const call of calls){
        let result,args;
        try{args=JSON.parse(call.arguments||"{}");result=this.tool(call.name,args);}
        catch(e){result={error:"Malformed tool arguments"};}
        trace.push({tool:call.name,arguments:args||{},result});
        input.push({type:"function_call_output",call_id:call.call_id,output:JSON.stringify(result)});
      }
    }
    return {answer:"Stopped after six model steps. Review the trace; no further actions ran.",trace,pending:this.store.snapshot().pending};
  }
}
