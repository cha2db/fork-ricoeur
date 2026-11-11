"""Autonomous deterministic ranking and core-proximity gates."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"ux_lab"))
from rank_candidates import rank
data=rank(ROOT/"ux_lab/candidates.json")
rows=data["ranking"]
assert len(rows)>=10
assert len({r["id"] for r in rows})==len(rows)
assert rows==sorted(rows,key=lambda x:(-x["score_preliminary"],x["id"]))
assert rows[0]["score_preliminary"] >= next(r for r in rows if r["id"]=="ricoeur")["score_preliminary"]
assert all(r["tested"] is False for r in rows)
assert all(0<=r["score_preliminary"]<=100 for r in rows)
assert next(r for r in rows if r["id"]=="kept")["core"]<next(r for r in rows if r["id"]=="ricoeur")["core"]
assert next(r for r in rows if r["id"]=="chatvault")["core"]<next(r for r in rows if r["id"]=="textual")["core"]
assert data["baseline"]["search"]=="FTS5"
print("PASS UX-010: 9 gates; deterministic preliminary rank, baseline core comparison, no false test claims")
