# UX Lab — autonomous, read-only adapter ports

The existing Ricoeur SQLite database is the single source of data. The UX lab does not migrate or write it. Each port is independent:
- `python ux_lab/ux.py --db PATH capabilities`
- `python ux_lab/ux.py --db PATH conversations --query docker --platform chatgpt`
- `python ux_lab/ux.py --db PATH transcript CONVERSATION_ID`
- `python ux_lab/ux.py --db PATH graph --query docker`
- `python ux_lab/ux.py --db PATH serve --port 8765` (local HTTP + embedded browser GUI)
- `python ux_lab/test_autonomous.py` (temporary synthetic SQLite, 3 conversations, tests all ports)

All outputs except `serve` are versioned JSON. `serve` binds **127.0.0.1** only; static UI consumes the same Python CLI functions through HTTP, never SQL. Graph edges are explicitly **shared-query hits**, not semantic claims. No inferred knowledge edges. The real graph requires the search/relation contract from the other branch.

Dependencies: Python 3.10+ stdlib only for UX lab. Existing Ricoeur CLI/TUI remain untouched. No production DB writes.

Optional frontends evaluated, not embedded: Kept (React/Tauri/Rust/CozoDB), LLM Chat Vault (JS/Python/SQLite), Vue Flow, Cytoscape. Core is **not equivalent**: Kept uses Markdown vault + CozoDB, Vault has its own SQLite schema and branch resolver; Ricoeur uses SQLite conversations/messages and FTS5. Do not replace storage just to adopt a UI.

Test on tablet (same Wi-Fi): for security, do not expose this dev HTTP server on LAN. Run on a trusted machine and forward 127.0.0.1 via an authenticated tunnel, or use local browser on machine. No auth is implemented; not production-ready.
