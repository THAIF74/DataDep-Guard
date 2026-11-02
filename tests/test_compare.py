from datadep_guard.compare import compare_manifests
def test_detect_all_file_changes():
    old = {
        "files": [
            {"path": "data.csv", "sha256": "aaa"},
            {"path": "image.png", "sha256": "bbb"},
            {"path": "notes.txt", "sha256": "ccc"},
        ]
    }
    new = {
        "files": [
            {"path": "data.csv", "sha256": "aaa"},
            {"path": "image.png", "sha256": "changed"},
            {"path": "new_file.csv", "sha256": "ddd"},
        ]
    }
    result = compare_manifests(old, new)
    assert result["added"] == ["new_file.csv"]
    assert result["removed"] == ["notes.txt"]
    assert result["modified"] == ["image.png"]
    assert result["unchanged"] == ["data.csv"]
    assert result["status"] == "CHANGES DETECTED"
def test_no_changes():
    manifest = {
        "files": [
            {"path": "data.csv", "sha256": "aaa"}
        ]
    }
    result = compare_manifests(manifest, manifest)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []
    assert result["unchanged"] == ["data.csv"]
    assert result["status"] == "NO CHANGES"
def test_empty_manifests():
    result = compare_manifests(
        {"files": []},
        {"files": []}
    )
    assert result["status"] == "NO CHANGES"
    assert result["unchanged"] == []
def test_all_files_added():
    result = compare_manifests(
        {"files": []},
        {
            "files": [
                {"path": "one.csv", "sha256": "aaa"},
                {"path": "two.csv", "sha256": "bbb"},
            ]
        }
    )
    assert result["added"] == ["one.csv", "two.csv"]
    assert result["removed"] == []
