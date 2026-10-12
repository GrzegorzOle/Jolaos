from jolaos import i18n
from jolaos.heads import build_heads


def test_every_head_has_texts_in_every_language():
    for code in i18n.LANGUAGES:
        i18n.set_language(code)
        for head in build_heads():
            for field in ("title", "desc", "restore"):
                text = i18n.head_text(head.id, field)
                assert text and not text.endswith(f".{field}"), (code, head.id, field)
            for note in head.notes:
                assert i18n.t(note) != note, (code, head.id, note)
    i18n.set_language(i18n.DEFAULT_LANGUAGE)


def test_english_covers_polish_keys():
    assert set(i18n._EN) == set(i18n._PL)
