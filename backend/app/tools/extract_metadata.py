import fitz


def extract_metadata(pdf_path: str) -> dict[str, str | None]:
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    doc.close()
    return {
        "title": metadata.get("title"),
        "author": metadata.get("author"),
        "subject": metadata.get("subject"),
        "keywords": metadata.get("keywords"),
    }
