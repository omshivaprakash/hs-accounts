"""Text extraction. Digital PDFs use their embedded text layer; scans and photos go through tesseract."""
from pathlib import Path

MIN_TEXT = 40  # shortcut: fewer chars than this is treated as a scanned PDF and OCR'd


def _tesseract(images):
    import pytesseract

    texts, confs = [], []
    for im in images:
        data = pytesseract.image_to_data(im, output_type=pytesseract.Output.DICT)
        confs += [float(c) for w, c in zip(data["text"], data["conf"]) if w.strip() and float(c) >= 0]
        texts.append(pytesseract.image_to_string(im))
    return "\n".join(texts), (sum(confs) / len(confs) / 100 if confs else 0.0)


def extract_text(path):
    """Return (text, confidence 0..1). Digital PDFs score 1.0."""
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        from pypdf import PdfReader

        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
        if len(text.strip()) >= MIN_TEXT:
            return text, 1.0
        from pdf2image import convert_from_path

        return _tesseract(convert_from_path(str(p), dpi=200))
    from PIL import Image

    return _tesseract([Image.open(p)])
