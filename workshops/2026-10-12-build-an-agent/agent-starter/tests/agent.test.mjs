import test from "node:test";
import assert from "node:assert/strict";
import {mkdtemp, writeFile, rm} from "node:fs/promises";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {LeadStore} from "../store.mjs";
import {LeadAgent} from "../agent.mjs";

const seeds=[{id:"L-001",name:"Jamie Sample",stage:"New",notes:"Unanswered inquiry",contact_permission:"Yes",next_follow_up:"2026-10-12"}];
async function setup(t){
  const dir=await mkdtemp(join(tmpdir(),"scoopos-agent-test-"));
  t.after(()=>rm(dir,{recursive:true,force:true}));
  const seed=join(dir,"seed.json"),file=join(dir,"state/leads.json"),instructions=join(dir,"agent.md");
  await writeFile(seed,JSON.stringify(seeds));
  await writeFile(instructions,"You are a test agent. Read records. Propose only. Never send.");
  const store=new LeadStore({file,seed});await store.init();
  return {dir,store,instructions};
}
function mock(...outputs){let calls=0;return async ()=>({ok:true,status:200,json:async()=>{const d=outputs[calls++];if(!d)throw Error("Unexpected model call");return d;}});}
const message=text=>({output:[{type:"message",role:"assistant",content:[{type:"output_text",text}]}]});
const call=(name,args)=>({output:[{type:"function_call",call_id:"call_test",name,arguments:JSON.stringify(args)}]});

test("agent reads actual sandbox lead using a model function call",async t=>{
  const {store,instructions}=await setup(t);
  const agent=new LeadAgent({store,key:"fake-for-test",fetchImpl:mock(call("get_lead",{lead_id:"L-001"}),message("Jamie needs a reply; price is unknown.")),instructionsFile:instructions});
  const out=await agent.ask("Find Jamie");
  assert.equal(out.trace.length,1);
  assert.equal(out.trace[0].tool,"get_lead");
  assert.equal(out.trace[0].result.record.id,"L-001");
  assert.match(out.answer,/price is unknown/);
});
test("AI tool only proposes: no record write until owner approves",async t=>{
  const {store,instructions}=await setup(t);
  const agent=new LeadAgent({store,key:"fake-for-test",fetchImpl:mock(call("propose_lead_update",{lead_id:"L-001",stage:"Needs Reply",next_follow_up:"2026-10-13",note:"Draft ready, not sent",reason:"Unanswered inquiry"}),message("Awaiting owner approval.")),instructionsFile:instructions});
  const out=await agent.ask("Update Jamie");
  assert.equal(store.get("L-001").stage,"New");
  assert.equal(out.pending.length,1);
  const result=await store.approve(out.pending[0].approval_id);
  assert.equal(result.status,"approved_and_saved");
  assert.equal(store.get("L-001").stage,"Needs Reply");
  assert.equal(store.get("L-001").next_follow_up,"2026-10-13");
  assert.equal((await store.approve(out.pending[0].approval_id)).error,"Approval not found or already used");
});
test("bad and stale changes are rejected",async t=>{
  const {store}=await setup(t);
  assert.ok(store.propose({lead_id:"L-001",stage:"Oops",next_follow_up:"",note:"",reason:"test"}).error);
  assert.ok(store.propose({lead_id:"L-001",stage:"New",next_follow_up:"2026-02-30",note:"",reason:"test"}).error);
  const p=store.propose({lead_id:"L-001",stage:"Needs Reply",next_follow_up:"",note:"",reason:"test"}).proposal;
  store.get("L-001").stage="Lost";
  assert.match((await store.approve(p.approval_id)).error,/changed/);
});
