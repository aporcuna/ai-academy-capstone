import pytest
from langchain_core.documents import Document

from data_storage.document_loader import load_chunks_from_directory


HEADER_SEPARATOR = "-" * 20


def write_chunk_file(
    directory,
    file_name,
    *,
    source="glossary.md",
    chunk_id="0",
    source_type="glossary",
    content="Chunk body",
):
    file_path = directory / file_name
    file_path.write_text(
        f"METADATA_SOURCE: {source}\n"
        f"METADATA_CHUNK_ID: {chunk_id}\n"
        f"METADATA_TYPE: {source_type}\n"
        f"{HEADER_SEPARATOR}\n"
        f"{content}",
        encoding="utf-8",
    )
    return file_path


def test_returns_empty_list_for_empty_directory(tmp_path, capsys):
    documents = load_chunks_from_directory(str(tmp_path))

    assert documents == []
    assert "Parsing 0 chunk files" in capsys.readouterr().out


def test_loads_single_chunk_with_metadata(tmp_path):
    write_chunk_file(
        tmp_path,
        "glossary_md_chunk_000.txt",
        source="glossary.md",
        chunk_id="0",
        source_type="glossary",
        content="A glossary entry.",
    )

    documents = load_chunks_from_directory(str(tmp_path))

    assert len(documents) == 1
    document = documents[0]
    assert isinstance(document, Document)
    assert document.page_content == "A glossary entry."
    assert document.metadata == {
        "source": "glossary.md",
        "chunk_id": "0",
        "chunk_file": "glossary_md_chunk_000.txt",
        "source_type": "glossary",
    }


def test_excludes_metadata_header_from_page_content(tmp_path):
    content = "Given a user\nWhen they log in\nThen they see the dashboard"
    write_chunk_file(tmp_path, "chunk.txt", content=content)

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.page_content == content
    assert "METADATA_SOURCE" not in document.page_content
    assert HEADER_SEPARATOR not in document.page_content


def test_preserves_multiline_content_and_trailing_newline(tmp_path):
    content = "First line\n\nThird line\n"
    write_chunk_file(tmp_path, "chunk.txt", content=content)

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.page_content == content


def test_preserves_unicode_content(tmp_path):
    content = "Cafe \u2615 \u2014 \u65e5\u672c\u8a9e \U0001f680"
    write_chunk_file(tmp_path, "chunk.txt", content=content)

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.page_content == content


def test_empty_body_produces_empty_page_content(tmp_path):
    write_chunk_file(tmp_path, "chunk.txt", content="")

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.page_content == ""


def test_ignores_non_txt_files(tmp_path):
    write_chunk_file(tmp_path, "keep.txt")
    (tmp_path / "ignore.md").write_text("markdown", encoding="utf-8")
    (tmp_path / "ignore.feature").write_text("feature", encoding="utf-8")
    (tmp_path / "ignore.json").write_text("{}", encoding="utf-8")

    documents = load_chunks_from_directory(str(tmp_path))

    assert [document.metadata["chunk_file"] for document in documents] == ["keep.txt"]


def test_loads_multiple_chunk_files(tmp_path):
    write_chunk_file(
        tmp_path,
        "first.txt",
        source="glossary.md",
        chunk_id="0",
        source_type="glossary",
        content="First chunk",
    )
    write_chunk_file(
        tmp_path,
        "second.txt",
        source="testing_guide.md",
        chunk_id="1",
        source_type="testing_guide",
        content="Second chunk",
    )
    write_chunk_file(
        tmp_path,
        "third.txt",
        source="login.feature",
        chunk_id="2",
        source_type="gherkin_example",
        content="Third chunk",
    )

    documents = load_chunks_from_directory(str(tmp_path))

    assert len(documents) == 3
    by_file = {document.metadata["chunk_file"]: document for document in documents}
    assert set(by_file) == {"first.txt", "second.txt", "third.txt"}
    assert by_file["first.txt"].page_content == "First chunk"
    assert by_file["second.txt"].metadata["source_type"] == "testing_guide"
    assert by_file["third.txt"].metadata["source"] == "login.feature"


def test_preserves_metadata_values_containing_spaces_and_paths(tmp_path):
    source = "data/existing features/login feature.feature"
    source_type = "gherkin example"
    write_chunk_file(
        tmp_path,
        "chunk.txt",
        source=source,
        chunk_id="007",
        source_type=source_type,
    )

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.metadata["source"] == source
    assert document.metadata["source_type"] == source_type
    assert document.metadata["chunk_id"] == "007"


def test_preserves_content_that_resembles_metadata(tmp_path):
    content = "METADATA_SOURCE: literal text\n--------------------\nEnd"
    write_chunk_file(tmp_path, "chunk.txt", content=content)

    document = load_chunks_from_directory(str(tmp_path))[0]

    assert document.page_content == content


def test_accepts_pathlib_directory(tmp_path):
    write_chunk_file(tmp_path, "chunk.txt")

    documents = load_chunks_from_directory(tmp_path)

    assert len(documents) == 1


def test_raises_for_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_chunks_from_directory(str(tmp_path / "missing"))
