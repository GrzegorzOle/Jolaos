from jolaos.journal import Journal


def test_record_keeps_first_previous(tmp_path):
    journal = Journal(tmp_path / "journal.json")
    journal.record("x", {"a": 1})
    journal.record("x", {"a": 2})
    assert journal.get("x")["previous"] == {"a": 1}
    assert journal.applied_ids() == ["x"]


def test_forget_and_persist(tmp_path):
    path = tmp_path / "journal.json"
    journal = Journal(path)
    journal.record("x", None)
    journal.set_config("language", "en")
    reloaded = Journal(path)
    assert reloaded.has("x")
    assert reloaded.get_config("language") == "en"
    reloaded.forget("x")
    assert not Journal(path).has("x")


def test_broken_file_is_tolerated(tmp_path):
    path = tmp_path / "journal.json"
    path.write_text("{not json", encoding="utf-8")
    journal = Journal(path)
    assert journal.applied_ids() == []
