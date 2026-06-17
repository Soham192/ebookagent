import fitz


def analyze_pdf(pdf_path: str) -> dict[str, int | bool]:
    doc = fitz.open(pdf_path)
    try:
        scanned_pages = 0
        for page in doc:
            text = page.get_text().strip()
            if len(text) < 50:
                scanned_pages += 1
        return {
            "pages": doc.page_count,
            "scanned_pages": scanned_pages,
            "requires_ocr": scanned_pages > 0,
        }
    finally:
        doc.close()
