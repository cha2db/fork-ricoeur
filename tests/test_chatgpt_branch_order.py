"""The export's explicit children list, not mapping iteration order, selects the branch."""
from ricoeur.importers.chatgpt import _walk_messages


def test_selected_branch_ignores_mapping_insertion_order():
    mapping = {
        "root": {"parent": None, "children": ["m0"], "message": None},
        "m0": {"parent": "root", "children": ["m1"], "message": {"id": "a", "author": {"role": "user"}, "content": {"parts": ["start"]}}},
        "m1": {"parent": "m0", "children": ["side", "m2"], "message": {"id": "b", "author": {"role": "assistant"}, "content": {"parts": ["middle"]}}},
        "m2": {"parent": "m1", "children": [], "message": {"id": "c", "author": {"role": "assistant"}, "content": {"parts": ["selected"]}}},
        "side": {"parent": "m1", "children": [], "message": {"id": "d", "author": {"role": "assistant"}, "content": {"parts": ["not selected"]}}},
    }
    assert [m["id"] for m in _walk_messages({"mapping": mapping})] == ["a", "b", "c"]
