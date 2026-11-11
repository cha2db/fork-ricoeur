"""UX-012: rank/category matrix integrity; not a third-party runtime smoke test."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"ux_lab"))
from rank_candidates import rank

data=rank(ROOT/"ux_lab/candidates.json")
rows=data["ranking"]
ids={row["id"] for row in rows}
assert len(rows)==27 and len(ids)==27
assert rows==sorted(rows,key=lambda x:(-x["score_preliminary"],x["id"]))
assert data["weights"]=={"core":40,"ui":30,"adapter":20,"license":10}
assert all(0<=r["score_preliminary"]<=100 for r in rows)
assert all(r["tested"] is False for r in rows)
assert {"llmchatsarchive","centralchat","threadshelf","threadline","chatsearch","agenthistory","contextflow"}<=ids
assert set(data["search_mode_index"]) >= {"fts5","semantic","graph","fuzzy"}
assert set(data["presentation_mode_index"]) >= {"graph","split-pane","tui"}
assert all(len(r["search_modes"])>0 and len(r["presentation_modes"])>0 for r in rows)
assert all(r["core"]<=3 for r in rows if r["category"] in ("app-web","commercial-extension"))
assert all(r["license_status"]!="proprietary" for r in rows if r["adoption_status"]=="existing")
assert next(r for r in rows if r["id"]=="centralchat")["core"] < next(r for r in rows if r["id"]=="ricoeur")["core"]
assert len(data["ranking_by_category"]) >= 6
print("PASS UX-012: 13 gates; 27 distinct candidates, per-category rankings, search GUI matrices")
