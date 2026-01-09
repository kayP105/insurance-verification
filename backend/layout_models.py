from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image
import pytesseract
import torch

processor = LayoutLMv3Processor.from_pretrained(
    "microsoft/layoutlmv3-base",
    apply_ocr=False
)
model = LayoutLMv3ForTokenClassification.from_pretrained(
    "microsoft/layoutlmv3-base"
)
model.eval()

def extract_words_and_boxes(image_pil):
    """
    Uses Tesseract to get words + bounding boxes
    """
    if image_pil.mode != "RGB":
        image_pil = image_pil.convert("RGB")

    data = pytesseract.image_to_data(image_pil, output_type=pytesseract.Output.DICT)

    words = []
    boxes = []

    w, h = image_pil.size

    n = len(data["text"])
    for i in range(n):
        text = data["text"][i].strip()
        if text == "":
            continue

        x, y, bw, bh = (
            data["left"][i],
            data["top"][i],
            data["width"][i],
            data["height"][i],
        )

        # Normalize boxes to 0–1000 range (LayoutLM format)
        x0 = int(1000 * x / w)
        y0 = int(1000 * y / h)
        x1 = int(1000 * (x + bw) / w)
        y1 = int(1000 * (y + bh) / h)

        words.append(text)
        boxes.append([x0, y0, x1, y1])

    return words, boxes


def extract_layout_entities(image_pil, ocr_text=None):
    """
    Runs LayoutLMv3 on real OCR words + bounding boxes
    """

    words, boxes = extract_words_and_boxes(image_pil)

    if len(words) == 0:
        return {"warning": "No OCR words found for LayoutLM"}

    encoding = processor(
        image_pil,
        words,
        boxes=boxes,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=512,
    )

    with torch.no_grad():
        outputs = model(**encoding)

    predictions = outputs.logits.argmax(-1).squeeze().tolist()

    return {
        "status": "success",
        "num_words": len(words),
        "num_tokens": len(predictions) if isinstance(predictions, list) else 1,
        "note": "LayoutLMv3 ran on real OCR words + boxes"
    }
