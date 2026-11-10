#!/usr/bin/env bash
# HTTP local: interface no navegador do tablet; acesso remoto exige protecao.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[[ -x "$PY" ]] || { echo "Ambiente .venv ausente"; exit 2; }
case "${1:-start}" in
 setup)
  "$PY" -m pip install 'fastapi>=0.110' 'uvicorn>=0.27'
  ;;
 check)
  "$PY" -c 'from ricoeur.http_adapter import app; print("HTTP adapter: OK",len(app.routes),"routes")'
  ;;
 start)
  "$PY" -c 'from ricoeur.http_adapter import app; print("HTTP adapter: OK")' || {
    echo "Execute antes: bash _dev/web.sh setup"; exit 2;
  }
  echo "Abra no navegador do TABLET: http://127.0.0.1:8765"
  exec "$PY" -m uvicorn ricoeur.http_adapter:app --host 127.0.0.1 --port 8765
  ;;
 *) echo "Uso: bash _dev/web.sh setup|check|start"; exit 2;;
esac
