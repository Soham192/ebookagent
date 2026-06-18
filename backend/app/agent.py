from pathlib import Path
import shutil
from typing import TypedDict

from app.tools.analyze_pdf import PdfAnalysis, analyze_pdf
from app.tools.run_ocr import run_ocr
from app.tools.extract_metadata import extract_metadata
from app.tools.convert_document import convert_document


class ProcessResult(TypedDict):
    output_path: str
    format: str
    title: str
    author: str
    requires_ocr: bool
    ocr_error: str | None


class Agent:
    async def process_pdf(
        self,
        pdf_path: Path | str,
        metadata: dict[str, str | None],
        output_format: str = "azw3",
        output_name: str | None = None,
    ) -> ProcessResult:
        pdf_path = Path(pdf_path)
        original_pdf_path = pdf_path
        analysis = analyze_pdf(pdf_path)

        ocr_error = None
        if analysis["requires_ocr"]:
            ocr_pdf_path = pdf_path.parent / f"{pdf_path.stem}_ocr.pdf"
            try:
                run_ocr(pdf_path, ocr_pdf_path)
                pdf_path = ocr_pdf_path
            except RuntimeError as exc:
                ocr_error = str(exc)

        extracted = extract_metadata(pdf_path)
        title = metadata.get("title") or extracted.get("title") or "Unknown Title"
        author = metadata.get("author") or extracted.get("author") or "Unknown Author"

        output_name = output_name or pdf_path.stem
        output_path = pdf_path.parent.parent / "outputs" / f"{output_name}.{output_format}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # If the user requested PDF, skip conversion and just copy the original PDF.
        if output_format == "pdf":
            shutil.copy2(pdf_path, output_path)
            return {
                "output_path": str(output_path),
                "format": "pdf",
                "title": title,
                "author": author,
                "requires_ocr": analysis["requires_ocr"],
                "ocr_error": ocr_error,
            }

        try:
            convert_document(
                pdf_path,
                output_path,
                title=title,
                author=author,
                output_format=output_format,
            )
        except RuntimeError as conversion_error:
            normalized_pdf_path = original_pdf_path.parent / f"{original_pdf_path.stem}_normalized.pdf"
            try:
                run_ocr(original_pdf_path, normalized_pdf_path, force=True)
                convert_document(
                    normalized_pdf_path,
                    output_path,
                    title=title,
                    author=author,
                    output_format=output_format,
                )
                ocr_error = ocr_error or "Direct conversion failed; succeeded after OCR normalization."
            except RuntimeError as fallback_error:
                raise RuntimeError(
                    f"{conversion_error} OCR normalization fallback also failed: {fallback_error}"
                ) from fallback_error

        return {
            "output_path": str(output_path),
            "format": output_format,
            "title": title,
            "author": author,
            "requires_ocr": analysis["requires_ocr"],
            "ocr_error": ocr_error,
        }
