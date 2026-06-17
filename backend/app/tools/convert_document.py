import subprocess
from pathlib import Path


def convert_document(input_pdf: str, output_path: str, title: str, author: str, output_format: str) -> None:
    output_path = Path(output_path)
    command = [
        "ebook-convert",
        str(input_pdf),
        str(output_path),
        "--title",
        title,
        "--authors",
        author,
    ]
    try:
        subprocess.run(command, check=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Conversion tool not found. Please install Calibre and ensure ebook-convert is available."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Document conversion failed: {exc}. Verify the format is supported and Calibre is installed."
        ) from exc
