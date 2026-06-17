import subprocess
from pathlib import Path


def run_ocr(input_pdf: str, output_pdf: str) -> None:
    input_pdf = Path(input_pdf)
    output_pdf = Path(output_pdf)

    command = [
        "ocrmypdf",
        "--skip-text",
        str(input_pdf),
        str(output_pdf),
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "OCR tool not found. Please install ocrmypdf and tesseract."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"OCR processing failed: {exc}. Ensure ocrmypdf is installed and the PDF can be processed."
        ) from exc
