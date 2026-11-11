import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import {performance} from "node:perf_hooks";
import {PGlite} from "@electric-sql/pglite";

const [fixtureFile,reportFile]=process.argv.slice(2);
if(!fixtureFile||!reportFile)throw Error("Usage: node runner.mjs fixture.json report.json");
const fixture=JSON.parse(fs.readFileSync(fixtureFile,"utf8"));
const root=fs.mkdtempSync(path.join(os.tmpdir(),"cha2db-pglite-"));
const dataDir=path.join(root,"pgdata");
const report={status:"RUNNING",candidate:"PGlite",input_hash:fixture.sha256,
 storage:"PostgreSQL WASM, persisted to filesystem in Node.js",
 dataset:{representative_messages:fixture.documents.length,
         branch_messages:5,synthetic:true,human_gold:false},
 tests:{},queries:[]};
const branch=[
 ["branch-m1","conv-branch1",null,"How did we choose the storage?"],
 ["branch-m2","conv-branch1","branch-m1","Keep source with markerunique2026"],
 ["branch-m3","conv-branch1","branch-m1","Alternative reply, separate branch"],
 ["branch-a1","conv-branch2",null,"Can FTS5 find messages?"],
 ["branch-a2","conv-branch2","branch-a1","FTS5 supports lexical queries"]
];
const getBytes=(dir)=>fs.existsSync(dir)?
  fs.readdirSync(dir,{withFileTypes:true}).reduce((sum,file)=>{
    const filename=path.join(dir,file.name);
    return sum+(file.isDirectory()?getBytes(filename):fs.statSync(filename).size);
  },0):0;
let db;
try{
 let start=performance.now();
 db=await PGlite.create({dataDir});
 await db.exec(`CREATE TABLE IF NOT EXISTS messages(
   id TEXT PRIMARY KEY,conv_id TEXT NOT NULL,parent_id TEXT,content TEXT NOT NULL
 );`);
 await db.exec("CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conv_id)");
 await db.exec("CREATE INDEX IF NOT EXISTS idx_messages_fts ON messages USING GIN (to_tsvector('simple',content))");
 const prepared=fixture.documents.map(x=>[x.id,x.conv_id,null,x.content]).concat(branch);
 const batch=async()=>{
  await db.transaction(async tx=>{
   for(const row of prepared)
     await tx.query("INSERT INTO messages(id,conv_id,parent_id,content) VALUES($1,$2,$3,$4) ON CONFLICT(id) DO NOTHING",row);
  });
 };
 await batch();
 report.import_seconds=Number(((performance.now()-start)/1000).toFixed(3));
 const before=(await db.query("SELECT count(*)::int AS n FROM messages")).rows[0].n;
 await batch();
 const after=(await db.query("SELECT count(*)::int AS n FROM messages")).rows[0].n;
 report.tests.idempotent_on_conflict=before===1005 && after===before;
 for(const q of ["SSH","PostgreSQL","AUoK","markerunique2026","doesnotexist999"]) {
  start=performance.now();
  const found=await db.query(
   "SELECT id,conv_id FROM messages WHERE to_tsvector('simple',content) @@ plainto_tsquery('simple',$1) ORDER BY id LIMIT 20",[q]);
  report.queries.push({query:q,hits:found.rows.length,latency_ms:Number((performance.now()-start).toFixed(3))});
 }
 report.tests.fts_retrieval=report.queries.find(x=>x.query==="SSH").hits>0
   &&report.queries.find(x=>x.query==="doesnotexist999").hits===0
   &&report.queries.find(x=>x.query==="markerunique2026").hits===1;
 await db.close();db=null;
 db=await PGlite.create({dataDir});
 const persisted=await db.query("SELECT id,parent_id,content FROM messages WHERE conv_id='conv-branch1' ORDER BY id");
 report.tests.branch_siblings_preserved=persisted.rows.length===3
  && persisted.rows.filter(x=>x.parent_id==="branch-m1").length===2;
 const repeat=(await db.query("SELECT count(*)::int AS n FROM messages")).rows[0].n;
 report.tests.persisted_after_reopen=repeat===1005;
 report.tests.original_ids_preserved=(await db.query(
   "SELECT count(*)::int AS n FROM messages WHERE id LIKE 'fixture-cha2db-v1-m%'")).rows[0].n===1000;
 report.tests.unique_source_marker=(await db.query(
   "SELECT count(*)::int AS n FROM messages WHERE content LIKE '%markerunique2026%'")).rows[0].n===1;
 report.storage_bytes=getBytes(dataDir);
 report.status=Object.values(report.tests).every(Boolean)?"PASS":"FAIL";
 report.verdict="WASM_POSTGRES_PERSISTENCE_AND_FTS_ONLY_NO_BROWSER_OR_ANDROID_TEST";
}catch(e){
 report.status="BLOCKED";
 report.error=String(e?.stack??e);
}finally{
 if(db)await db.close().catch(()=>{});
 fs.rmSync(root,{recursive:true,force:true});
}
report.limitations=[
 "Runs Node.js PGlite with filesystem, not IndexedDB in browser.",
 "Indexing 1000 representative messages from the same 40k synthetic SQLite fixture plus a five-message branching fixture.",
 "No concurrency, syncing, large-scale benchmark or corpus of human-labeled chats.",
 "No runtime integration into Cha2db or Phase3 UX."
];
fs.writeFileSync(reportFile,JSON.stringify(report,null,2));
console.log(JSON.stringify({status:report.status,tests:report.tests,
 import_seconds:report.import_seconds,storage_bytes:report.storage_bytes,
 error:report.error?.slice(0,1200)},null,2));
if(report.status!=="PASS")process.exit(1);
