import subprocess

from jolaos import winapi


def test_program_path_is_quoted():
    path = winapi.program_path()
    assert path.startswith('"') and path.endswith('"')
    # schtasks /TR dostaje calosc jako jeden argument z wewnetrznymi cudzyslowami
    line = subprocess.list2cmdline([path + " --guard"])
    assert line.startswith('"\\"')


def test_value_matches_binary_is_case_insensitive():
    assert winapi.value_matches({"kind": "binary", "data": "00ab"}, "binary", b"\x00\xab")
    assert not winapi.value_matches(None, "dword", 1)
    assert not winapi.value_matches({"kind": "sz", "data": "1"}, "dword", 1)
