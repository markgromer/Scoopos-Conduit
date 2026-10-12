import {randomUUID} from "node:crypto";
import {readFile, writeFile, mkdir} from "node:fs/promises";
import {dirname} from "node:path";

const stages = new Set(["New","Needs Reply","Quote Sent","Waiting","Paused","Won","Lost"]);

export class LeadStore {
  constructor({file,seed}) {
    this.file=file; this.seed=seed; this.leads=[]; this.pending=new Map();
  }
  async init(){
    await mkdir(dirname(this.file),{recursive:true});
    try{this.leads=JSON.parse(await readFile(this.file,"utf8"));}
    catch(e){
      if(e.code!=="ENOENT")throw e;
      this.leads=JSON.parse(await readFile(this.seed,"utf8"));
      await this.save();
    }
    if(!Array.isArray(this.leads)||this.leads.some(x=>!x||typeof x.id!=="string"))throw Error("Invalid sandbox data file");
  }
  async save(){await writeFile(this.file,JSON.stringify(this.leads,null,2)+"\n",{mode:0o600});}
  get(id){return this.leads.find(l=>l.id===id)||null;}
  list(stage=""){
    return this.leads.filter(l=>!stage||l.stage===stage);
  }
  propose({lead_id,stage="",next_follow_up="",note="",reason=""}){
    const lead=this.get(lead_id);
    if(!lead)return {status:"not_found",lead_id};
    if(typeof stage!=="string"||typeof note!=="string"||typeof reason!=="string"||typeof next_follow_up!=="string")return {error:"Invalid field types"};
    if(stage&&!stages.has(stage))return {error:"Invalid stage"};
    if(next_follow_up&&!isDate(next_follow_up))return {error:"Date must be a valid YYYY-MM-DD date"};
    if(note.length>300||reason.length>500||!reason.trim())return {error:"Reason required; note max 300, reason max 500 characters"};
    if(!stage&&!next_follow_up&&!note.trim())return {error:"No proposed changes"};
    const changes={};
    if(stage&&lead.stage!==stage)changes.stage=stage;
    if(next_follow_up&&lead.next_follow_up!==next_follow_up)changes.next_follow_up=next_follow_up;
    if(note.trim()&&lead.notes!==note)changes.notes=note;
    if(!Object.keys(changes).length)return {status:"no_change_needed"};
    const approval_id=randomUUID();
    const proposal={approval_id,lead_id,before:Object.fromEntries(Object.keys(changes).map(k=>[k,lead[k]])),changes,reason,created_at:new Date().toISOString()};
    this.pending.set(approval_id,proposal);
    return {status:"awaiting_human_approval",proposal};
  }
  async approve(approval_id){
    const p=this.pending.get(approval_id);
    if(!p)return {error:"Approval not found or already used"};
    const lead=this.get(p.lead_id);
    if(!lead)return {error:"Lead no longer exists"};
    for(const [key,value] of Object.entries(p.before))if(lead[key]!==value)return {error:"Lead changed since proposal; refresh before approving"};
    Object.assign(lead,p.changes);
    await this.save();
    this.pending.delete(approval_id);
    return {status:"approved_and_saved",lead_id:lead.id,changes:p.changes};
  }
  dismiss(approval_id){const existed=this.pending.delete(approval_id);return {status:existed?"dismissed":"not_found"};}
  snapshot(){return {leads:this.leads,pending:[...this.pending.values()]};}
}
function isDate(date){
  if(!/^\d{4}-\d{2}-\d{2}$/.test(date))return false;
  const d=new Date(date+"T00:00:00.000Z");
  return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===date;
}
