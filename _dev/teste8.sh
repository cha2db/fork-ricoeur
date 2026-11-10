#!/usr/bin/env bash
# Teste 8: acionamento remoto pelo celular (Termius -> SSH -> Termux -> MCP).
# O cliente MCP executa no tablet; isto NAO prova transporte MCP sobre SSH.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
mkdir -p _dev/results
echo "== Teste 8: acionamento remoto de MCP pelo celular =="
if [[ -z "${SSH_CONNECTION:-}" && -z "${SSH_CLIENT:-}" ]]; then
  echo "FAIL: execute a partir de uma sessao SSH (Termius no celular)."
  exit 2
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "FAIL: .venv/bin/python nao encontrado; execute _dev/remote.sh check."
  exit 2
fi
echo "SSH remoto: PASS"
echo "SDK MCP e servidor:"
.venv/bin/python -c 'from mcp import ClientSession; from ricoeur.mcp_adapter import build_server; build_server(); print("MCP imports: PASS")'
echo "Cliente MCP real, busca e leitura de mensagens:"
set +e
.venv/bin/python -u _dev/teste7.py 2>&1 | tee _dev/results/teste8.log
status=${PIPESTATUS[0]}
set -e
if [[ "$status" -ne 0 ]]; then
  echo "Teste 8: FAIL (status $status)."
  exit "$status"
fi
.venv/bin/python - <<'PY'
import json
from pathlib import Path
p = Path("_dev/results/teste7.json")
report = json.loads(p.read_text())
report["test"] = 8
report["remote_invocation"] = "Termius -> SSH -> tablet"
report["mcp_transport"] = "stdio local no tablet"
report["remote_mcp_transport_validated"] = False
Path("_dev/results/teste8.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
assert report["status"] == "PASS"
print("Teste 8: PASS — MCP real acionado remotamente via SSH.")
print("Limite: cliente e servidor MCP executaram no tablet; MCP via SSH ainda pendente.")
PY
