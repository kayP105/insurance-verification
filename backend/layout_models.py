from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image

processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")

def extract_layout_entities(pdf_path):
    image = Image.open(pdf_path)
    words = ["Policy", "Number", "123456"]
    boxes = [[50, 50, 150, 80], [200, 50, 300, 80], [350, 50, 450, 80]]
    encoding = processor(image, words, boxes=boxes, return_tensors="pt")
    outputs = model(**encoding)
    return str(outputs)

