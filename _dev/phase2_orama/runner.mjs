import fs from "node:fs";
import {performance} from "node:perf_hooks";
import {create,insert,search} from "@orama/orama";

const [fixturePath,outPath]=process.argv.slice(2);
if(!fixturePath||!outPath) throw new Error("node runner.mjs fixture.json report.json");
const fixture=JSON.parse(fs.readFileSync(fixturePath,"utf8"));
let report={status:"RUNNING",candidate:"Orama",source:fixturePath,
  sha256:fixture.sha256,documents:fixture.documents.length,
  note:"JS browser/edge candidate; no LLM and no live Cha2db integration",queries:[]};
try {
  const labels=new Map(fixture.documents.map(d=>[d.id,
     Number(d.conv_id.split("c").at(-1))%10]));
  const db=await create({schema:{id:"string",content:"string",platform:"string"}});
  let t=performance.now();
  for(const doc of fixture.documents) await insert(db,{
     id:doc.id,content:doc.content,platform:"synthetic"});
  report.build_seconds=Number(((performance.now()-t)/1000).toFixed(3));
  const times=[];
  for(const q of fixture.queries){
    t=performance.now();
    const response=await search(db,{term:q.text,properties:["content"],limit:10});
    const latency=performance.now()-t;
    const hits=response.hits.map(hit=>hit.document.id);
    if(hits.length>10 || new Set(hits).size!==hits.length || hits.some(id=>!labels.has(id)))
      throw new Error("invalid hit IDs: "+q.text);
    const precision=hits.filter(id=>labels.get(id)===q.topic).length/10;
    report.queries.push({query:q.text,topic:q.topic,p10:precision,
      latency_ms:Number(latency.toFixed(3)),hits});
    times.push(latency);
  }
  times.sort((a,b)=>a-b);
  report.median_latency_ms=Number(((times[4]+times[5])/2).toFixed(3));
  report.mean_p10=Number((report.queries.reduce((a,x)=>a+x.p10,0)/10).toFixed(4));
  report.status="PASS";
  report.verdict="TECHNICAL_EXECUTION_ONLY_NO_HUMAN_GOLD";
}catch(err){
  report.status="BLOCKED";
  report.error=String(err?.stack??err);
}
report.limitations=["Synthetic repeated 1000 docs, not all 40k messages indexed",
  "No HTTP/MCP, semantic model or production integration",
  "Index persistence, update costs and browser memory not measured"];
fs.writeFileSync(outPath,JSON.stringify(report,null,2));
console.log(JSON.stringify({status:report.status,mean_p10:report.mean_p10,
  build_seconds:report.build_seconds,median_latency_ms:report.median_latency_ms,
  error:report.error?.slice(0,1000)},null,2));
if(report.status!=="PASS")process.exit(1);
