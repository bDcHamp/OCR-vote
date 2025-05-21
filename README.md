# OCR Voting API

This script is provides a Flask-based API to extract the serial number and selected candidates from scanned ballot paper images using OCR and image processing.

## Setup

1. **Clone the repository or copy the files to your project folder.**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Tesseract OCR:**
   - Download and install from: https://github.com/tesseract-ocr/tesseract
   - Make sure `tesseract` is in your system PATH, or set the path in `ocr_vote.py`.

## Running the API

```bash
python ocr_vote.py
```

The API will be available at `http://localhost:5000/api/ocr-vote`.

## API Usage

- **Endpoint:** `/api/ocr-vote`
- **Method:** `POST`
- **Form Data:**
  - `image`: The ballot paper image file (JPG, PNG, etc.)

**Example using `curl`:**
```bash
curl -X POST -F "image=@/path/to/your/ballot.jpg" http://localhost:5000/api/ocr-vote
```

**Response:**
```json
{
  "serial_number": "298",
  "selected_candidates": [
    {"name": "Micle Jo", "membership": "A/C XYZ/1"},
    {"name": "Micle", "membership": "A/C XYZ/2"},
    ...
  ]
}
```

## Notes
- For production, set `debug=False` in `ocr_vote.py`.
- Call this API from your Laravel backend using HTTP requests and process the JSON response as needed.