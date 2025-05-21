from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/ocr-vote', methods=['POST'])
def ocr_vote():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    image = cv2.imread(filepath)
    if image is None:
        return jsonify({'error': 'Invalid image file'}), 400
    serial = extract_serial_number(image)
    tick_boxes = detect_tick_boxes(image)
    candidates = extract_candidates(image, tick_boxes)
    os.remove(filepath)
    return jsonify({
        'serial_number': serial,
        'selected_candidates': candidates
    })

def extract_serial_number(image):
    h, w = image.shape[:2]
    serial_crop = image[80:130, 400:600]  # Adjust as needed
    text = pytesseract.image_to_string(serial_crop, config='--psm 7')
    for line in text.split('\n'):
        if line.strip().isdigit():
            return line.strip()
    return None

def detect_tick_boxes(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    tick_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect = w / float(h)
        area = w * h
        if 0.8 < aspect < 1.2 and 30 < w < 60 and 30 < h < 60 and area > 1000:
            roi = thresh[y:y+h, x:x+w]
            filled = cv2.countNonZero(roi) / (w * h)
            if filled > 0.2:
                tick_boxes.append((x, y, w, h))
    return tick_boxes

def get_ocr_data(image):
    return pytesseract.image_to_data(image, output_type=Output.DICT)

def extract_candidates(image, tick_boxes):
    ocr_data = get_ocr_data(image)
    candidates = []
    for (x, y, w, h) in tick_boxes:
        for i in range(len(ocr_data['text'])):
            tx, ty, tw, th = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            if tx > x + w and abs(ty - y) < 30 and tw > 50:
                text = ocr_data['text'][i].strip()
                if text and "A/C" in text:
                    name = text.split("A/C")[0].strip()
                    membership = "A/C" + text.split("A/C")[1].strip()
                    candidates.append({"name": name, "membership": membership})
    return candidates

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 