from datadep_guard import __version__
from datadep_guard.cli import main


def test_version_is_set():
    assert __version__ == "0.1.0"


def test_cli_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["datadep-guard", "--version"])

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0

    assert "0.1.0" in capsys.readouterr().out
