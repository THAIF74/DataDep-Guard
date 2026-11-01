
import hashlib
import json
import pytest

from datadep_guard.manifest import (
    calculate_sha256,
    create_manifest,
    save_manifest,
)


def test_calculate_sha256(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world", encoding="utf-8")

    expected = hashlib.sha256(b"hello world").hexdigest()

    assert calculate_sha256(file_path) == expected


def test_create_manifest(tmp_path):
    (tmp_path / "data.txt").write_text("dataset", encoding="utf-8")

    manifest = create_manifest(
        "example/dataset",
        "a" * 40,
        tmp_path,
    )

    assert manifest["dataset"] == "example/dataset"
    assert manifest["revision"] == "a" * 40
    assert manifest["file_count"] == 1
    assert manifest["files"][0]["path"] == "data.txt"
    assert manifest["files"][0]["sha256"] == hashlib.sha256(
        b"dataset"
    ).hexdigest()


def test_manifest_includes_nested_files(tmp_path):
    nested = tmp_path / "images"
    nested.mkdir()
    (nested / "image.txt").write_text("image data")

    manifest = create_manifest("example/data", "abc", tmp_path)

    assert manifest["file_count"] == 1
    assert manifest["files"][0]["path"] == "images/image.txt"


def test_empty_directory(tmp_path):
    manifest = create_manifest("example/empty", "abc", tmp_path)

    assert manifest["file_count"] == 0
    assert manifest["files"] == []


def test_missing_directory(tmp_path):
    with pytest.raises(ValueError):
        create_manifest(
            "example/missing",
            "abc",
            tmp_path / "missing",
        )


def test_save_manifest(tmp_path):
    manifest = {
        "dataset": "example/data",
        "file_count": 0,
        "files": [],
    }

    output = tmp_path / "snapshots" / "manifest.json"
    save_manifest(manifest, output)

    saved = json.loads(output.read_text(encoding="utf-8"))

    assert saved["dataset"] == "example/data"
    assert saved["file_count"] == 0

def test_manifest_excludes_cache_files(tmp_path):
    (tmp_path / "data.txt").write_text("real dataset")

    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "cached.pyc").write_bytes(b"cache data")

    (tmp_path / "temporary.pyc").write_bytes(b"compiled data")

    manifest = create_manifest("example/data", "abc", tmp_path)

    assert manifest["file_count"] == 1
    assert manifest["files"][0]["path"] == "data.txt"
