from jolaos.heads import COPILOT_KEY_SCANCODE, build_scancode_map, parse_scancode_map


def test_roundtrip_empty():
    assert parse_scancode_map(None) == []
    assert parse_scancode_map(b"") == []
    assert parse_scancode_map(build_scancode_map([])) == []


def test_build_disables_copilot_key_only():
    raw = build_scancode_map([(COPILOT_KEY_SCANCODE, 0)])
    assert raw == bytes.fromhex("00000000" "00000000" "02000000" "00006e00" "00000000")
    assert parse_scancode_map(raw) == [(COPILOT_KEY_SCANCODE, 0)]


def test_existing_entries_are_preserved():
    # Caps Lock (0x3A) -> Left Ctrl (0x1D), zapis znany z dokumentacji
    caps_to_ctrl = bytes.fromhex("00000000" "00000000" "02000000" "1d003a00" "00000000")
    entries = parse_scancode_map(caps_to_ctrl)
    assert entries == [(0x3A, 0x1D)]
    entries.append((COPILOT_KEY_SCANCODE, 0))
    rebuilt = build_scancode_map(entries)
    assert parse_scancode_map(rebuilt) == [(0x3A, 0x1D), (COPILOT_KEY_SCANCODE, 0)]


def test_garbage_is_ignored():
    assert parse_scancode_map(b"\x01\x02\x03") == []
    assert parse_scancode_map(bytes(13)) == []
