import fs from "node:fs";
import {performance} from "node:perf_hooks";
import MiniSearch from "minisearch";
import {Index as FlexIndex} from "flexsearch";
const [engine, fixturePath, outputPath] = process.argv.slice(2);
if(!["minisearch","flexsearch"].includes(engine) || !fixturePath || !outputPath)
  throw new Error("Usage node runner.mjs minisearch|flexsearch fixture.json output.json");
const fixture=JSON.parse(fs.readFileSync(fixturePath,"utf8"));
const documents=fixture.documents;
const labels=new Map(documents.map(d=>[d.id,Number(d.conv_id.split("c").at(-1))%10]));
const output={candidate:engine,status:"RUNNING",input_hash:fixture.sha256,
  documents:documents.length,query_count:fixture.queries.length,queries:[]};
try {
  const initialHeap=process.memoryUsage().heapUsed;
  const began=performance.now();
  let search;
  if(engine==="minisearch"){
    const index=new MiniSearch({fields:["content"],storeFields:[]});
    index.addAll(documents.map(d=>({id:d.id,content:d.content})));
    search=q=>index.search(q,{combineWith:"AND"}).slice(0,10).map(hit=>hit.id);
  } else {
    const index=new FlexIndex({tokenize:"forward"});
    for(let i=0;i<documents.length;i++)index.add(i+1,documents[i].content);
    search=q=>index.search(q,10).map(num=>documents[Number(num)-1].id);
  }
  output.build_seconds=Number(((performance.now()-began)/1000).toFixed(3));
  output.delta_heap_bytes=Math.max(0,process.memoryUsage().heapUsed-initialHeap);
  const samples=[];
  for(const q of fixture.queries){
    const t=performance.now();
    const hitIds=search(q.text);
    const duration=performance.now()-t;
    if(hitIds.length>10 || new Set(hitIds).size!==hitIds.length || hitIds.some(id=>!labels.has(id)))
      throw new Error("Foreign or duplicate canonical IDs: "+q.text);
    samples.push(duration);
    output.queries.push({query:q.text,topic:q.topic,hits:hitIds,
      p10:Number((hitIds.filter(id=>labels.get(id)===q.topic).length/10).toFixed(4)),
      latency_ms:Number(duration.toFixed(3))});
  }
  samples.sort((a,b)=>a-b);
  output.median_latency_ms=Number(((samples[4]+samples[5])/2).toFixed(3));
  output.mean_p10=Number((output.queries.reduce((a,q)=>a+q.p10,0)/output.queries.length).toFixed(4));
  output.status="PASS";
  output.verdict="ENGINE_EXECUTES_NOT_SELECTED_OR_HUMAN_VALIDATED";
}catch(error){
  output.status="BLOCKED";
  output.error=String(error?.stack??error);
}
output.limitations=["One representative message per conversation, synthetic fixture",
 "No persistence, incremental updates, index serialization or ACL benchmark",
 "No full 40k ranking benchmark and no human relevance gold",
 "Heap delta reflects Node process only, noisy and not comparable across runners"];
fs.writeFileSync(outputPath,JSON.stringify(output,null,2));
console.log(JSON.stringify({candidate:engine,status:output.status,mean_p10:output.mean_p10,
  median_latency_ms:output.median_latency_ms,build_seconds:output.build_seconds,
  error:output.error?.slice(0,900)},null,2));
if(output.status!=="PASS")process.exit(1);
