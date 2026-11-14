"""Fresh-checkout and tampered-source regressions for the native API verifier."""

import base64
import hashlib
import io
import json
from unittest.mock import Mock

import pytest

from tools import verify_native_climate


@pytest.fixture
def source_blob(monkeypatch):
    raw = b"# synthetic official-source response\n"
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    entry = {"path": "homeassistant/example.py", "blob": digest}
    monkeypatch.setattr(verify_native_climate, "SOURCE_BLOBS", [entry])
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    return raw, entry


def test_fresh_download_is_verified_written_and_reused(
    tmp_path, monkeypatch, source_blob
):
    raw, entry = source_blob
    response = io.BytesIO(
        json.dumps(
            {"encoding": "base64", "content": base64.b64encode(raw).decode()}
        ).encode()
    )
    fetch = Mock(return_value=response)
    monkeypatch.setattr(verify_native_climate.urllib.request, "urlopen", fetch)
    verify_native_climate.ensure_sources(tmp_path)
    assert (tmp_path / entry["path"]).read_bytes() == raw
    assert fetch.call_count == 1
    fetch.side_effect = AssertionError(
        "A verified cached blob must not be downloaded again"
    )
    verify_native_climate.ensure_sources(tmp_path)
    assert fetch.call_count == 1


def test_bad_download_is_never_persisted(tmp_path, monkeypatch, source_blob):
    _, entry = source_blob
    response = io.BytesIO(
        json.dumps(
            {
                "encoding": "base64",
                "content": base64.b64encode(b"wrong source").decode(),
            }
        ).encode()
    )
    monkeypatch.setattr(
        verify_native_climate.urllib.request, "urlopen", Mock(return_value=response)
    )
    with pytest.raises(RuntimeError, match="blob verification failed"):
        verify_native_climate.ensure_sources(tmp_path)
    assert not (tmp_path / entry["path"]).exists()


def test_bad_cached_blob_fails_without_network(tmp_path, monkeypatch, source_blob):
    _, entry = source_blob
    path = tmp_path / entry["path"]
    path.parent.mkdir(parents=True)
    path.write_bytes(b"modified cached source")
    fetch = Mock(side_effect=AssertionError("A bad cached blob must fail closed"))
    monkeypatch.setattr(verify_native_climate.urllib.request, "urlopen", fetch)
    with pytest.raises(RuntimeError, match="blob verification failed"):
        verify_native_climate.ensure_sources(tmp_path)
    fetch.assert_not_called()
