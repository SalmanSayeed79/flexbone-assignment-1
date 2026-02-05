# OCR API - Image Text Extraction Service

A powerful FastAPI-based OCR (Optical Character Recognition) service that uses Google Cloud Vision API to extract text and metadata from images. It supports both single-image processing and batch processing.

## 🚀 Features

- **Single OCR**: Extract text and confidence scores from individual images.
- **Batch Processing**: Process up to 20 images in a single request.
- **Metadata Extraction**: Automatically extracts file size, image format, dimensions, and EXIF data.
- **Interactive Web UI**: A clean, responsive frontend to test the OCR functionality.
- **Dockerized**: Ready for deployment using Docker.
- **CORS Enabled**: Cross-Origin Resource Sharing is enabled for all origins.

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **OCR Engine**: Google Cloud Vision API
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Deployment**: Docker

## 📋 Prerequisites

- Python 3.9+
- A Google Cloud Platform (GCP) account.
- Google Cloud Vision API enabled.
- Service Account credentials (JSON) with Vision API permissions.

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd flexbone
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory and add your Google Cloud credentials path:
```env
GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"
```

### 5. Google Cloud Service Account
Ensure your `service-account.json` file is placed in the project directory (and added to `.gitignore`) or specify its absolute path in the `.env` file.

## 🏃 Running the Application

### Locally
Start the FastAPI server:
```bash
python main.py
```
The API will be available at `http://localhost:8000`.
The interactive documentation (Swagger UI) can be found at `http://localhost:8000/docs`.

### Using Docker
1. **Build the image**:
   ```bash
   docker build -t ocr-api .
   ```
2. **Run the container**:
   ```bash
   docker run -p 8080:8080 --env-file .env ocr-api
   ```

## 🔌 API Endpoints

### 1. Perform OCR (Single)
Extracts text from a single image.

- **URL**: `/ocr`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Payload**:
  - `file`: The image file (JPG, JPEG, PNG). Max size: 5MB.

**Example Response**:
```json
{
  "text": "Extracted text content...",
  "confidence": 98.5,
  "metadata": {
    "file_size_kb": 150.2,
    "format": "JPEG",
    "width": 1920,
    "height": 1080,
    "exif": { ... }
  }
}
```

### 2. Perform Batch OCR
Extracts text from multiple images in one request.

- **URL**: `/ocr-batch`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Payload**:
  - `files`: Multiple image files (List of UploadFile). Max 20 files.

**Example Response**:
```json
{
  "results": [
    {
      "filename": "image1.jpg",
      "text": "Text from image 1",
      "confidence": 95.0,
      "metadata": { ... },
      "message": "Success"
    },
    ...
  ],
  "total_processed": 2,
  "successful_processed": 2
}
```

### 3. Web Interface
- **URL**: `/` or `/index.html`
- **Method**: `GET`
- **Description**: Serves the user-friendly frontend for the OCR service.

## 🛡️ Validation Rules

- **Max File Size**: 5MB per image.
- **Max Batch Size**: 20 images.
- **Supported Formats**: `.jpg`, `.jpeg`, `.png`.

## 📄 License
[MIT License](LICENSE)
