from pathlib import Path
import os
import shutil
from typing import TypedDict

from app.tools.analyze_pdf import PdfAnalysis, analyze_pdf
from app.tools.run_ocr import run_ocr
from app.tools.extract_metadata import extract_metadata
from app.tools.convert_document import convert_document


def log_step(task_id: str, message: str) -> None:
    print(f"[upload:{task_id}] {message}", flush=True)


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
        task_id = output_name or pdf_path.stem
        enable_ocr_fallback = os.getenv("ENABLE_OCR_FALLBACK", "false").lower() == "true"

        log_step(task_id, "analyzing PDF")
        analysis = analyze_pdf(pdf_path)
        log_step(task_id, f"analysis complete; requires_ocr={analysis['requires_ocr']}")

        ocr_error = None
        if analysis["requires_ocr"]:
            ocr_pdf_path = pdf_path.parent / f"{pdf_path.stem}_ocr.pdf"
            try:
                log_step(task_id, "starting OCR")
                run_ocr(pdf_path, ocr_pdf_path)
                pdf_path = ocr_pdf_path
                log_step(task_id, "OCR complete")
            except RuntimeError as exc:
                ocr_error = str(exc)
                log_step(task_id, f"OCR failed; continuing with original PDF: {ocr_error}")

        log_step(task_id, "extracting metadata")
        extracted = extract_metadata(pdf_path)
        title = metadata.get("title") or extracted.get("title") or "Unknown Title"
        author = metadata.get("author") or extracted.get("author") or "Unknown Author"

        output_name = task_id
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
            log_step(task_id, f"starting {output_format} conversion")
            convert_document(
                pdf_path,
                output_path,
                title=title,
                author=author,
                output_format=output_format,
            )
            log_step(task_id, "conversion complete")
        except RuntimeError as conversion_error:
            log_step(task_id, f"conversion failed: {conversion_error}")
            if not enable_ocr_fallback:
                raise RuntimeError(
                    f"{conversion_error} OCR fallback is disabled for faster failures. "
                    "Set ENABLE_OCR_FALLBACK=true to retry failed conversions with OCR normalization."
                ) from conversion_error

            normalized_pdf_path = original_pdf_path.parent / f"{original_pdf_path.stem}_normalized.pdf"
            try:
                log_step(task_id, "starting OCR normalization fallback")
                run_ocr(original_pdf_path, normalized_pdf_path, force=True)
                log_step(task_id, "OCR normalization complete; retrying conversion")
                convert_document(
                    normalized_pdf_path,
                    output_path,
                    title=title,
                    author=author,
                    output_format=output_format,
                )
                log_step(task_id, "fallback conversion complete")
                ocr_error = ocr_error or "Direct conversion failed; succeeded after OCR normalization."
            except RuntimeError as fallback_error:
                log_step(task_id, f"OCR fallback failed: {fallback_error}")
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
