import {createServer} from "node:http";
import {readFile} from "node:fs/promises";
import {fileURLToPath} from "node:url";
import {join,dirname} from "node:path";
import {LeadStore} from "./store.mjs";
import {LeadAgent} from "./agent.mjs";

const root=dirname(fileURLToPath(import.meta.url));
const port=Number(process.env.PORT||8788);
if(!Number.isInteger(port)||port<1||port>65535)throw Error("Invalid PORT");
const store=new LeadStore({file:join(root,"local-data/leads.json"),seed:join(root,"data/demo-leads.json")});
await store.init();
const agent=new LeadAgent({store,key:process.env.OPENAI_API_KEY||"",model:process.env.OPENAI_MODEL||"gpt-4.1-mini",instructionsFile:join(root,"agent-config.md")});
const html=await readFile(join(root,"ui.html"),"utf8");

function respond(res,status,obj){res.writeHead(status,{"content-type":"application/json; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff"});res.end(JSON.stringify(obj));}
function readJson(req){return new Promise((resolve,reject)=>{let chunks=[],len=0;req.on("data",c=>{len+=c.length;if(len>65536){reject(Error("Request exceeds 64 KB"));req.destroy();return;}chunks.push(c);});req.on("end",()=>{try{resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));}catch(e){reject(Error("Invalid JSON body"));}});req.on("error",reject);});}
const server=createServer(async(req,res)=>{
  try{
    const url=new URL(req.url||"/","http://localhost");
    if(req.headers.origin&&!/^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(req.headers.origin)){respond(res,403,{error:"Origin not allowed"});return;}
    if(req.method==="GET"&&url.pathname==="/"){
      res.writeHead(200,{"content-type":"text/html; charset=utf-8","cache-control":"no-store","content-security-policy":"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:","x-content-type-options":"nosniff"});
      res.end(html);return;
    }
    if(req.method==="GET"&&url.pathname==="/api/state"){respond(res,200,{...store.snapshot(),configured:!!process.env.OPENAI_API_KEY,model:agent.model});return;}
    if(req.method==="POST"){
      if(!String(req.headers["content-type"]||"").startsWith("application/json")){respond(res,415,{error:"Send application/json"});return;}
      const body=await readJson(req);
      if(url.pathname==="/api/chat"){
        const result=await agent.ask(body.message);respond(res,200,result);return;
      }
      if(url.pathname==="/api/approve"){
        if(body.confirm!==true){respond(res,400,{error:"Explicit confirmation required"});return;}
        respond(res,200,await store.approve(String(body.approval_id||"")));return;
      }
      if(url.pathname==="/api/dismiss"){
        respond(res,200,store.dismiss(String(body.approval_id||"")));return;
      }
    }
    respond(res,404,{error:"Not found"});
  }catch(e){const msg=e instanceof Error?e.message:"Unknown error";respond(res,400,{error:msg});}
});
server.listen(port,"127.0.0.1",()=>console.log("ScoopOS local agent ready: http://127.0.0.1:"+port+"\nDemo data only. Keep this server localhost-only."));
