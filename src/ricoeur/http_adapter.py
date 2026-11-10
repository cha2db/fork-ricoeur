"""Read-only local HTTP adapter over the same retrieval contract as MCP."""
import html
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from .db import get_connection
from .retrieval import search_messages, get_message_context

app = FastAPI(title="Cha2db/Ricoeur local search", version="0.1")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/search")
def search(q: str, limit: int = Query(20, ge=1, le=200),
           context: int = Query(1, ge=0, le=10),
           platform: Optional[str] = None):
    conn = get_connection()
    try:
        return search_messages(conn, q, limit, context, platform)
    except (ValueError, Exception) as exc:
        if isinstance(exc, ValueError) or exc.__class__.__name__ == "OperationalError":
            raise HTTPException(status_code=400, detail=str(exc))
        raise
    finally:
        conn.close()

@app.get("/api/messages/{message_id}")
def message(message_id: str, context: int = Query(2, ge=0, le=20)):
    conn = get_connection()
    try:
        result = get_message_context(conn, message_id, context)
        if result is None:
            raise HTTPException(status_code=404, detail="message not found")
        return result
    finally:
        conn.close()

@app.get("/", response_class=HTMLResponse)
def index():
    return """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cha2db · Busca local</title>
<style>
body{font:16px system-ui;background:#111827;color:#e5e7eb;max-width:850px;margin:auto;padding:18px}
input,button{font:inherit;padding:12px;border-radius:8px;border:1px solid #64748b}
input{background:#1f2937;color:white;width:min(75%,520px)}
button{background:#2563eb;color:white;cursor:pointer}
article{padding:14px;margin:12px 0;background:#1f2937;border-radius:10px}
small{color:#9ca3af}pre{white-space:pre-wrap;overflow-wrap:anywhere}
</style><h1>Cha2db · Busca local</h1>
<p>Busca por mensagens em múltiplas conversas. Sem LLM.</p>
<form id="form"><input id="q" placeholder="Consulta FTS5" required>
<button>Buscar</button></form><p id="status"></p><div id="results"></div>
<script>
const q=document.querySelector('#q'),status=document.querySelector('#status'),
results=document.querySelector('#results');
function el(tag,text){const n=document.createElement(tag);n.textContent=text??'';return n}
function showMessage(x){const a=el('article');a.append(el('small',x.role+' · '+x.id),el('pre',x.content));return a}
document.querySelector('#form').addEventListener('submit',async e=>{
 e.preventDefault();results.replaceChildren();status.textContent='Buscando...';
 try{
 const r=await fetch('/api/search?'+new URLSearchParams({q:q.value,context:'1'}));
 const data=await r.json();if(!r.ok)throw Error(data.detail||r.status);
 status.textContent=data.count+' mensagem(ns) encontrada(s)';
 for(const hit of data.hits){
  const a=el('article');a.append(el('h3',hit.conversation.title||hit.conversation.id),
  el('small',hit.conversation.platform+' · '+hit.conversation.id),showMessage(hit.message));
  const b=el('button','Mostrar contexto');
  b.addEventListener('click',async()=>{
   b.disabled=true;
   try{const r=await fetch('/api/messages/'+encodeURIComponent(hit.message.id)+'?context=3');
   if(!r.ok)throw Error(r.status);const data=await r.json();
   const d=el('div');d.append(el('h4','Antes'));
   data.before.forEach(m=>d.append(showMessage(m)));
   d.append(el('h4','Depois'));data.after.forEach(m=>d.append(showMessage(m)));
   b.replaceWith(d)}catch(err){b.disabled=false;status.textContent=String(err)}
  });a.append(b);results.append(a)
 }
 }catch(err){status.textContent='Erro: '+err.message}
});
</script></html>"""
