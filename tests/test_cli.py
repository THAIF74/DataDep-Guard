import json

from datadep_guard.cli import main


def test_version(capsys):
    assert main(["--version"]) == 0
    assert "datadep-guard 0.1.0" in capsys.readouterr().out


def test_scan_reports_unpinned_dataset(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    config = {
        "datasets": [
            {"source": "huggingface", "id": "ylecun/mnist", "revision": None}
        ]
    }
    (tmp_path / "datadep.json").write_text(json.dumps(config), encoding="utf-8")

    assert main(["scan"]) == 0
    output = capsys.readouterr().out
    assert "ylecun/mnist" in output
    assert "UNPINNED" in output
    assert "WARNING" in output


def test_scan_reports_pinned_dataset(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    config = {
        "datasets": [
            {"source": "huggingface", "id": "ylecun/mnist", "revision": "abc123"}
        ]
    }
    (tmp_path / "datadep.json").write_text(json.dumps(config), encoding="utf-8")

    assert main(["scan"]) == 0
    output = capsys.readouterr().out
    assert "PINNED" in output
    assert "abc123" in output


def test_scan_rejects_invalid_configuration(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "datadep.json").write_text('{"datasets": "invalid"}', encoding="utf-8")

    assert main(["scan"]) == 2
    assert "ERROR" in capsys.readouterr().err