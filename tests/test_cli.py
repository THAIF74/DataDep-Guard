import json

from datadep_guard.cli import main


def write_config(tmp_path, config):
    path = tmp_path / "datadep.json"
    path.write_text(json.dumps(config), encoding="utf-8")
    return path


def test_version(capsys):
    assert main(["--version"]) == 0
    assert "datadep-guard 0.1.0" in capsys.readouterr().out


def test_scan_checks_latest_for_unpinned_dataset(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.chdir(tmp_path)
    write_config(tmp_path, {
        "datasets": [
            {"source": "huggingface", "id": "ylecun/mnist", "revision": None}
        ]
    })

    def fake_fetch(dataset_id, revision=None):
        assert dataset_id == "ylecun/mnist"
        assert revision is None
        return {"id": dataset_id, "sha": "latestcommit123"}

    monkeypatch.setattr("datadep_guard.cli.fetch_dataset_info", fake_fetch)

    assert main(["scan"]) == 0
    output = capsys.readouterr().out
    assert "[UNPINNED] ylecun/mnist" in output
    assert "latestcommit123" in output
    assert "WARNING" in output
    assert "1 successful, 0 failed" in output


def test_scan_resolves_pinned_revision(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    write_config(tmp_path, {
        "datasets": [
            {"source": "huggingface", "id": "ylecun/mnist", "revision": "abc123"}
        ]
    })

    def fake_fetch(dataset_id, revision=None):
        assert revision == "abc123"
        return {"id": dataset_id, "sha": "abc123fullcommit"}

    monkeypatch.setattr("datadep_guard.cli.fetch_dataset_info", fake_fetch)

    assert main(["scan"]) == 0
    output = capsys.readouterr().out
    assert "[PINNED] ylecun/mnist" in output
    assert "Requested revision: abc123" in output
    assert "Resolved commit: abc123fullcommit" in output


def test_scan_reports_remote_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    write_config(tmp_path, {
        "datasets": [
            {"source": "huggingface", "id": "missing/dataset", "revision": None}
        ]
    })

    def fake_fetch(dataset_id, revision=None):
        raise RuntimeError("Dataset not found")

    monkeypatch.setattr("datadep_guard.cli.fetch_dataset_info", fake_fetch)

    assert main(["scan"]) == 1
    output = capsys.readouterr().out
    assert "[ERROR] missing/dataset" in output
    assert "1 failed" in output


def test_scan_rejects_invalid_configuration(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    write_config(tmp_path, {"datasets": "invalid"})

    assert main(["scan"]) == 2
    assert "ERROR" in capsys.readouterr().err


def test_scan_rejects_invalid_json(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "datadep.json").write_text("{invalid", encoding="utf-8")

    assert main(["scan"]) == 2
    assert "ERROR" in capsys.readouterr().err
