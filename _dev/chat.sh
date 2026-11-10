#!/usr/bin/env bash
# Gradio/ChatInterface + FastAPI. Optional heavy dependency experiment on Termux.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
[[ -x "$PY" ]] || { echo "FAIL: .venv ausente"; exit 2; }
mkdir -p _dev/results
case "${1:-start}" in
 setup)
   echo "Instalando Gradio no venv existente (pode falhar em dependencias nativas Termux)..."
   set +e
   "$PY" -m pip install 'gradio>=5,<7' 2>&1 | tee _dev/results/gradio-install.log
   rc=${PIPESTATUS[0]}
   set -e
   if [[ "$rc" -ne 0 ]]; then
     echo "BLOQUEIO DE INSTALACAO (exit $rc). Veja _dev/results/gradio-install.log"
     exit "$rc"
   fi
   "$PY" -c 'import gradio; print("Gradio import OK:",gradio.__version__)'
   ;;
 check)
   "$PY" -c 'from ricoeur.gradio_adapter import build_demo,answer; import gradio; print("Gradio:",gradio.__version__); print("ChatInterface:",type(build_demo()).__name__); print("Consulta:",answer("SQLite",[])[:150])'
   ;;
 start)
   "$PY" -c 'from ricoeur.gradio_adapter import build_app; build_app(); print("Gradio mounted: OK")' || { echo "Execute: bash _dev/chat.sh setup"; exit 2; }
   echo "Abra no navegador do TABLET: http://127.0.0.1:8766/chat"
   exec "$PY" -m ricoeur.gradio_adapter
   ;;
 *) echo "Uso: bash _dev/chat.sh setup|check|start"; exit 2 ;;
esac
