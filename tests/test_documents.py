"""Tests for DocumentClient."""

import io
import re

import pytest
import responses

from rezen.documents import DocumentClient, SignatureClient


class TestDocumentClient:
    """Test cases for DocumentClient."""

    def setup_method(self) -> None:
        """Set up client for tests."""
        self.client = DocumentClient(api_key="test_key")
        self.base_url = "https://arrakis.therealbrokerage.com/api/v1"

    def test_signature_client_alias(self) -> None:
        """SignatureClient is an alias of DocumentClient for backward compatibility."""
        assert SignatureClient is DocumentClient

    @responses.activate
    def test_post_document_without_file(self) -> None:
        """Test post_document without file uses JSON body."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents",
            json={"id": "doc-1"},
            status=201,
        )

        result = self.client.post_document({"title": "Contract"})
        assert result["id"] == "doc-1"
        assert b'"title": "Contract"' in responses.calls[0].request.body

    def test_post_document_with_file_uses_multipart(self) -> None:
        """Test post_document with file delegates to _request with files."""
        file_obj = io.BytesIO(b"pdf")
        called = {}

        def fake_request(method, endpoint, data=None, files=None, **_kwargs):  # type: ignore[no-untyped-def]
            called["method"] = method
            called["endpoint"] = endpoint
            called["data"] = data
            called["files"] = files
            return {"ok": True}

        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(self.client, "_request", fake_request)
            result = self.client.post_document({"title": "X"}, file=file_obj)

        assert result == {"ok": True}
        assert called["method"] == "POST"
        assert called["endpoint"] == "documents"
        assert called["data"] == {"title": "X"}
        assert "file" in called["files"]

    @responses.activate
    def test_get_document(self) -> None:
        """Test get_document endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/documents/doc-1",
            json={"id": "doc-1"},
            status=200,
        )

        assert self.client.get_document("doc-1") == {"id": "doc-1"}

    @responses.activate
    def test_get_document_status(self) -> None:
        """Test get_document_status endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/documents/doc-1/status",
            json={"status": "PENDING"},
            status=200,
        )

        assert self.client.get_document_status("doc-1") == {"status": "PENDING"}

    @responses.activate
    def test_send_document_for_signature(self) -> None:
        """Test send_document_for_signature endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/doc-1/send",
            json={"ok": True},
            status=200,
        )

        assert self.client.send_document_for_signature("doc-1", {"signers": []}) == {
            "ok": True
        }

    @responses.activate
    def test_cancel_signature_request(self) -> None:
        """Test cancel_signature_request endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/doc-1/cancel",
            json={"ok": True},
            status=200,
        )

        assert self.client.cancel_signature_request("doc-1") == {"ok": True}

    @responses.activate
    def test_remind_signer_with_and_without_message(self) -> None:
        """Test remind_signer uses message when provided, else empty dict."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/doc-1/signers/s1/remind",
            json={"ok": True},
            status=200,
        )
        assert self.client.remind_signer("doc-1", "s1") == {"ok": True}
        assert responses.calls[0].request.body == b"{}"

        responses.reset()
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/doc-1/signers/s1/remind",
            json={"ok": True},
            status=200,
        )
        assert self.client.remind_signer("doc-1", "s1", message="please sign") == {
            "ok": True
        }
        assert b'"message": "please sign"' in responses.calls[0].request.body

    @responses.activate
    def test_download_document(self) -> None:
        """Test download_document endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/documents/doc-1/download",
            json={"url": "x"},
            status=200,
        )
        assert self.client.download_document("doc-1") == {"url": "x"}

    @responses.activate
    def test_get_audit_trail(self) -> None:
        """Test get_audit_trail endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/documents/doc-1/audit-trail",
            json={"events": []},
            status=200,
        )
        assert self.client.get_audit_trail("doc-1") == {"events": []}

    @responses.activate
    def test_get_document_templates(self) -> None:
        """Test get_document_templates endpoint with pagination."""
        responses.add(
            responses.GET,
            re.compile(f"{re.escape(self.base_url)}/documents/templates.*"),
            json={"templates": []},
            status=200,
        )
        assert self.client.get_document_templates(page_number=1, page_size=10) == {
            "templates": []
        }
        url = responses.calls[0].request.url
        assert "pageNumber=1" in url
        assert "pageSize=10" in url

    @responses.activate
    def test_create_document_from_template(self) -> None:
        """Test create_document_from_template endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/templates/t1/create",
            json={"id": "doc-1"},
            status=200,
        )
        assert self.client.create_document_from_template("t1", {"x": 1}) == {
            "id": "doc-1"
        }

    @responses.activate
    def test_bulk_send_documents(self) -> None:
        """Test bulk_send_documents endpoint."""
        responses.add(
            responses.POST,
            f"{self.base_url}/documents/bulk-send",
            json={"ok": True},
            status=200,
        )
        assert self.client.bulk_send_documents([{"id": "d1"}]) == {"ok": True}

    @responses.activate
    def test_get_signer_link(self) -> None:
        """Test get_signer_link endpoint."""
        responses.add(
            responses.GET,
            f"{self.base_url}/documents/doc-1/signers/s1/link",
            json={"url": "link"},
            status=200,
        )
        assert self.client.get_signer_link("doc-1", "s1") == {"url": "link"}
