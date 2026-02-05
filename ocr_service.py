import os
from google.cloud import vision
from google.oauth2 import service_account
from dotenv import load_dotenv
from PIL import Image
from PIL.ExifTags import TAGS
import io

load_dotenv()

class OCRService:
    def __init__(self, credentials_path: str = None):
        """
        Initialize the OCR Service.
        :param credentials_path: Path to the Google Cloud service account JSON file.
                                  If None, it will try to use GOOGLE_APPLICATION_CREDENTIALS env var.
        """
        if credentials_path and os.path.exists(credentials_path):
            self.client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
        else:
            # This will use the default credentials if configured (e.g. via GOOGLE_APPLICATION_CREDENTIALS)
            self.client = vision.ImageAnnotatorClient()

    def extract_text(self, image_content: bytes) -> dict:
        """
        Extract text from image bytes using Google Cloud Vision OCR.
        Returns a dictionary with 'text' and 'confidence'.
        """
        image = vision.Image(content=image_content)
        
        # Performs text detection on the image file
        # We use document_text_detection for better structural info and confidence scores
        response = self.client.document_text_detection(image=image)
        
        # Log the full response for debugging (converting to dict for easier reading)
        # In a real app, you might want to log to a file or logging service
        print("--- Vision API Response Log ---")
        # Using the proto message's __dict__ or just str(response)
        # print(vision.AnnotatorResults.pb(response.full_text_annotation)) 
        # A simpler way to see the structure:
        print(f"Detected text length: {len(response.full_text_annotation.text)}")
        print(response)
        
        if response.error.message:
            raise Exception(f"Google Cloud Vision OCR Error: {response.error.message}")

        if not response.full_text_annotation.text:
            return {"text": "", "confidence": 0.0}

        # Calculate average confidence
        # Vision API provides confidence for blocks, paragraphs, words, and symbols.
        # We'll take the average confidence of all pages detected.
        confidences = []
        for page in response.full_text_annotation.pages:
            confidences.append(page.confidence)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "text": response.full_text_annotation.text,
            "confidence": round(avg_confidence * 100, 2),
            "metadata": self.extract_metadata(image_content)
        }

    def extract_metadata(self, image_content: bytes) -> dict:
        """
        Extract metadata from image bytes.
        """
        metadata = {
            "file_size_kb": round(len(image_content) / 1024, 2)
        }
        try:
            img = Image.open(io.BytesIO(image_content))
            metadata.update({
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
            })
            
            # Extract EXIF data
            exif_data = img._getexif()
            if exif_data:
                exif = {}
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Handle bytes values in EXIF
                    if isinstance(value, bytes):
                        try:
                            value = value.decode(errors='replace')
                        except:
                            value = str(value)
                    exif[str(tag)] = str(value)
                metadata["exif"] = exif
        except Exception as e:
            metadata["error"] = f"Metadata extraction failed: {str(e)}"
        
        return metadata
