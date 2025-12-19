import cv2
from PIL import Image
import imagehash
import os

def tamper_score_image(img_path):
    img = Image.open(img_path).convert("RGB")
    hash_orig = imagehash.average_hash(img)
    tmp_path = "tmp_ela.jpg"
    img.save(tmp_path, "JPEG", quality=65)
    img_ela = Image.open(tmp_path)
    hash_ela = imagehash.average_hash(img_ela)
    score = hash_orig - hash_ela
    os.remove(tmp_path)
    return float(score)
