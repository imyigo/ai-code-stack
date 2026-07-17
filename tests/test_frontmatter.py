from __future__ import annotations

import pytest

from ai_code_stack.frontmatter import FrontmatterError, parse_frontmatter_bytes


def test_basic_frontmatter():
    data, body = parse_frontmatter_bytes(b"---\nname: foo\ndescription: bar\n---\nBody text\n")
    assert data == {"name": "foo", "description": "bar"}
    assert body == "Body text"


def test_out_of_order_keys():
    data, _ = parse_frontmatter_bytes(b"---\ndescription: bar\nname: foo\ntags: [a, b]\n---\n")
    assert data["name"] == "foo"
    assert data["tags"] == ["a", "b"]


def test_multiline_value():
    raw = b"---\nname: foo\ndescription: |\n  line one\n  line two\n---\n"
    data, _ = parse_frontmatter_bytes(raw)
    assert data["description"] == "line one\nline two"


def test_quoted_values():
    raw = b'---\nname: foo\ndescription: "has: a colon"\n---\n'
    data, _ = parse_frontmatter_bytes(raw)
    assert data["description"] == "has: a colon"


def test_arrays():
    raw = b"---\nname: foo\ntags:\n  - one\n  - two\n---\n"
    data, _ = parse_frontmatter_bytes(raw)
    assert data["tags"] == ["one", "two"]


def test_utf8_bom():
    raw = "---\nname: foo\n---\n".encode("utf-8-sig")
    data, _ = parse_frontmatter_bytes(raw)
    assert data["name"] == "foo"


def test_crlf_line_endings():
    raw = b"---\r\nname: foo\r\ndescription: bar\r\n---\r\nBody\r\n"
    data, body = parse_frontmatter_bytes(raw)
    assert data["name"] == "foo"
    assert "\r" not in body


def test_lf_line_endings():
    raw = b"---\nname: foo\n---\nBody\n"
    data, body = parse_frontmatter_bytes(raw)
    assert data["name"] == "foo"
    assert body == "Body"


def test_unquoted_colon_space_in_scalar_is_repaired():
    # Real vendor content (e.g. loop-design-check/SKILL.md): a free-text description
    # containing "Two actions: (1) ..." is invalid strict-YAML but unambiguous intent.
    raw = b"---\nname: foo\ndescription: Two actions: (1) do this, (2) do that\n---\n"
    data, _ = parse_frontmatter_bytes(raw)
    assert data["name"] == "foo"
    assert "Two actions" in data["description"]


def test_missing_opening_delimiter_raises():
    with pytest.raises(FrontmatterError):
        parse_frontmatter_bytes(b"name: foo\n---\n")


def test_missing_closing_delimiter_raises():
    with pytest.raises(FrontmatterError):
        parse_frontmatter_bytes(b"---\nname: foo\n")


def test_missing_name_raises():
    with pytest.raises(FrontmatterError):
        parse_frontmatter_bytes(b"---\ndescription: bar\n---\n")


def test_non_mapping_frontmatter_raises():
    with pytest.raises(FrontmatterError):
        parse_frontmatter_bytes(b"---\n- one\n- two\n---\n")
