"""Full account ZIP: multiple numbered conversation JSON files, no extraction."""
import json
import zipfile

from ricoeur.importers.chatgpt import _iter_conversations_with_progress


def test_numbered_account_zip(tmp_path):
    archive = tmp_path / "account-export.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("conversations.json", json.dumps([{"id": "first"}]))
        zf.writestr("nested/conversations-1.json", json.dumps([{"id": "second"}]))
        zf.writestr("nested/conversations_2.json", json.dumps([{"id": "third"}]))
        zf.writestr("user.json", '{"email":"private@example.invalid"}')
        zf.writestr("chat.html", "<html>not an import source</html>")
    items = list(_iter_conversations_with_progress(archive))
    assert {item["id"] for item, _ in items} == {"first", "second", "third"}
    assert len(items) == 3
    assert items[-1][1] <= 1.0
    assert items[-1][1] > 0.5
