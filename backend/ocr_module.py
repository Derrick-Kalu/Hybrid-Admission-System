"""
ocr_module.py — OCR-Based Document Verification
Bingham University Hybrid Admission Pre-Screening System

Uses OpenCV for image preprocessing and Pytesseract for text extraction,
matching the implementation described in Chapter 4.2.5.
"""

import cv2
import numpy as np
import pytesseract
import os
import re

# Tesseract executable path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def preprocess_image(image_path):
    """
    Preprocesses an image using OpenCV for improved OCR accuracy.
    Steps: grayscale conversion -> noise reduction -> contrast enhancement -> thresholding.
    Returns the preprocessed image as a NumPy array.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at path: {image_path}")

    # Step 1: Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Step 2: Noise reduction using median blur
    denoised = cv2.medianBlur(gray, 3)

    # Step 3: Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Step 4: Adaptive thresholding for better text separation
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    return thresh


def extract_text_from_image(image_path):
    """
    Extracts text from an image using Pytesseract after OpenCV preprocessing.
    Returns the extracted text string, or None on error.
    """
    try:
        preprocessed = preprocess_image(image_path)
        # Use PSM 6: Assume a single uniform block of text
        text = pytesseract.image_to_string(preprocessed, config='--psm 6')
        return text
    except Exception as e:
        print(f"OCR Error [{image_path}]: {e}")
        return None


def extract_jamb_score(text):
    """
    Attempts to extract the UTME total score from OCR text of a JAMB result slip.
    Looks for patterns like 'Total: 245', 'Score: 245', or standalone 3-digit numbers
    in the valid UTME range (100–400).
    Returns the extracted score as an integer, or None if not found.
    """
    if not text:
        return None

    # Pattern 1: "Total Score: 245" or "Total: 245"
    pattern1 = re.search(r'total\s*(?:score)?\s*[:\-]?\s*(\d{3})', text, re.IGNORECASE)
    if pattern1:
        score = int(pattern1.group(1))
        if 100 <= score <= 400:
            return score

    # Pattern 2: "Score: 245" or "Aggregate: 245"
    pattern2 = re.search(r'(?:score|aggregate|result)\s*[:\-]?\s*(\d{3})', text, re.IGNORECASE)
    if pattern2:
        score = int(pattern2.group(1))
        if 100 <= score <= 400:
            return score

    # Pattern 3: Any 3-digit number in the UTME range (last resort)
    all_numbers = re.findall(r'\b(\d{3})\b', text)
    candidates = [int(n) for n in all_numbers if 100 <= int(n) <= 400]
    if candidates:
        return max(set(candidates), key=candidates.count)

    return None


def verify_document(text, expected_keywords):
    """
    Checks if expected keywords (e.g., applicant name fragments) appear in OCR text.
    Returns a dictionary with verification status and any missing keywords.
    """
    if not text:
        return {'verified': False, 'reason': 'No text extracted from document.', 'missing_keywords': []}

    text_lower = text.lower()
    missing_keywords = [kw for kw in expected_keywords if kw and kw.lower() not in text_lower]
    is_verified = len(missing_keywords) == 0

    return {
        'verified': is_verified,
        'missing_keywords': missing_keywords
    }


def verify_jamb_document(text, applicant_name):
    """
    Validates a JAMB result slip by:
    1. Extracting the total UTME score via OCR.
    2. Verifying the applicant's name appears on the document.
    3. Checking for JAMB-specific keywords to detect non-JAMB documents.

    Returns dict: { verified, ocr_score, name_found, is_jamb_document, reason }
    """
    result = {
        'verified': False,
        'ocr_score': None,
        'name_found': False,
        'is_jamb_document': False,
        'reason': ''
    }

    if not text:
        result['reason'] = 'No text could be extracted from the uploaded document.'
        return result

    text_lower = text.lower()

    # Check for JAMB-specific keywords
    jamb_keywords = ['jamb', 'joint admissions', 'matriculation', 'utme', 'unified tertiary']
    result['is_jamb_document'] = any(kw in text_lower for kw in jamb_keywords)

    # Extract UTME score
    result['ocr_score'] = extract_jamb_score(text)

    # Verify applicant name (check at least first or last name)
    name_parts = [p.strip() for p in applicant_name.split() if len(p.strip()) > 2]
    result['name_found'] = any(part.lower() in text_lower for part in name_parts)

    # Determine overall verification status
    if not result['is_jamb_document']:
        result['reason'] = 'The uploaded document does not appear to be a valid JAMB result slip.'
    elif result['ocr_score'] is None:
        result['reason'] = 'Could not extract a valid UTME score. Ensure the image is clear and legible.'
    elif not result['name_found']:
        result['reason'] = 'Applicant name not found on the JAMB result slip.'
    else:
        result['verified'] = True
        result['reason'] = f"JAMB result verified. Extracted UTME score: {result['ocr_score']}."

    return result
