"""
ocr_module.py — OCR-Based Document Verification
Bingham University Hybrid Admission Pre-Screening System

Supports: JPG, PNG, BMP, TIFF, WEBP, and PDF uploads.
Verifies: JAMB result slips, WAEC O'Level results, NECO O'Level results.
Per Nigerian examination body standards (JAMB, WAEC Nigeria, NECO).
"""

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os
import re

# Tesseract executable path (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Supported file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'bmp', 'tiff', 'tif', 'webp'}


def allowed_file(filename):
    """Returns True if the file extension is in the allowed list."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _load_pages_from_file(file_path):
    """
    Loads a list of PIL Images from any supported format.
    PDFs are rendered page-by-page at 300 DPI using PyMuPDF.
    Returns a list of PIL Images, or None on failure.
    """
    ext = os.path.splitext(file_path)[1].lower().lstrip('.')

    if ext == 'pdf':
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            doc.close()
            return images if images else None
        except ImportError:
            print("[OCR] PyMuPDF not installed. PDF support unavailable.")
            return None
        except Exception as e:
            print(f"[OCR] PDF load error [{file_path}]: {e}")
            return None
    else:
        try:
            return [Image.open(file_path)]
        except Exception as e:
            print(f"[OCR] Image load error [{file_path}]: {e}")
            return None


def _preprocess(img):
    """
    Converts PIL image to grayscale, enhances contrast, and sharpens for OCR.
    """
    try:
        img = img.convert('L')
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = img.filter(ImageFilter.SHARPEN)
        return img
    except Exception as e:
        print(f"[OCR] Preprocessing error: {e}")
        return None


def extract_text_from_image(file_path):
    """
    Extracts all text from any supported document (image or PDF).
    Multi-page PDFs have all pages concatenated.
    Returns the full extracted text string, or None on error.
    """
    try:
        pages = _load_pages_from_file(file_path)
        if not pages:
            return None

        all_text = []
        for img in pages:
            preprocessed = _preprocess(img)
            if preprocessed is None:
                continue
            text = pytesseract.image_to_string(preprocessed, config='--psm 6')
            all_text.append(text)

        return '\n'.join(all_text) if all_text else None
    except Exception as e:
        print(f"[OCR] Error [{file_path}]: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  SCORE EXTRACTION & DISCREPANCY DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_jamb_score(text):
    """
    Extracts the UTME total score from JAMB OCR text.
    Tries multiple regex patterns before falling back to candidate 3-digit numbers.
    """
    if not text:
        return None

    pattern1 = re.search(r'total\s*(?:score)?\s*[:\-]?\s*(\d{3})', text, re.IGNORECASE)
    if pattern1:
        score = int(pattern1.group(1))
        if 100 <= score <= 400:
            return score

    pattern2 = re.search(r'(?:score|aggregate|result)\s*[:\-]?\s*(\d{3})', text, re.IGNORECASE)
    if pattern2:
        score = int(pattern2.group(1))
        if 100 <= score <= 400:
            return score

    all_numbers = re.findall(r'\b(\d{3})\b', text)
    candidates = [int(n) for n in all_numbers if 100 <= int(n) <= 400]
    if candidates:
        return max(set(candidates), key=candidates.count)

    return None


def detect_score_discrepancy(declared_score, ocr_score, threshold=5):
    """
    Compares the applicant's declared UTME score against the OCR-extracted score.
    Per Nigerian admission integrity guidelines, a delta of more than 5 marks is flagged
    as a potential falsification and escalated for admin review.

    Returns a dict with:
      - flagged (bool): True if discrepancy exceeds threshold
      - delta (int|None): Absolute difference between scores
      - reason (str): Human-readable explanation
    """
    if declared_score is None or ocr_score is None:
        return {
            'flagged': False,
            'delta': None,
            'declared': declared_score,
            'ocr_extracted': ocr_score,
            'reason': 'Score comparison skipped — one or both values unavailable.'
        }

    delta = abs(int(declared_score) - int(ocr_score))
    flagged = delta > threshold

    return {
        'flagged': flagged,
        'delta': delta,
        'declared': int(declared_score),
        'ocr_extracted': int(ocr_score),
        'reason': (
            f'⚠️ Discrepancy detected: Declared score ({declared_score}) differs from '
            f'OCR-extracted score ({ocr_score}) by {delta} marks. '
            f'Escalated for manual admin verification per JAMB integrity policy.'
            if flagged else
            f'Scores are consistent. Declared: {declared_score}, OCR: {ocr_score} (Δ={delta}).'
        )
    }


# ─────────────────────────────────────────────────────────────────────────────
#  GENERIC KEYWORD VERIFIER
# ─────────────────────────────────────────────────────────────────────────────

def verify_document(text, expected_keywords):
    """
    Checks if all expected keywords appear in OCR-extracted text.
    Used for cross-checking applicant name on O'Level documents.
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


# ─────────────────────────────────────────────────────────────────────────────
#  JAMB RESULT VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def verify_jamb_document(text, applicant_name):
    """
    Validates an uploaded JAMB UTME result slip.

    Checks for:
    - JAMB-specific keywords (per JAMB official result format)
    - A valid 3-digit UTME score (100–400)
    - Applicant name presence on the document
    """
    result = {
        'verified': False,
        'ocr_score': None,
        'name_found': False,
        'is_jamb_document': False,
        'reason': ''
    }

    if not text:
        result['reason'] = 'No text could be extracted from the uploaded JAMB document.'
        return result

    text_lower = text.lower()

    jamb_keywords = [
        'jamb', 'joint admissions', 'matriculation', 'utme',
        'unified tertiary', 'joint admissions and matriculation'
    ]
    result['is_jamb_document'] = any(kw in text_lower for kw in jamb_keywords)
    result['ocr_score'] = extract_jamb_score(text)

    name_parts = [p.strip() for p in applicant_name.split() if len(p.strip()) > 2]
    result['name_found'] = any(part.lower() in text_lower for part in name_parts)

    if not result['is_jamb_document']:
        result['reason'] = 'Document does not appear to be a valid JAMB result slip. Ensure you upload the official JAMB print-out.'
    elif result['ocr_score'] is None:
        result['reason'] = 'Could not extract a valid UTME score. Ensure the document is clear and fully visible.'
    elif not result['name_found']:
        result['reason'] = 'Applicant name was not found on the JAMB result slip. Ensure you upload your own result.'
    else:
        result['verified'] = True
        result['reason'] = f"JAMB result verified. Extracted UTME score: {result['ocr_score']}."

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  WAEC O'LEVEL RESULT VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def verify_waec_document(text, applicant_name):
    """
    Validates an uploaded WAEC (West African Examinations Council) O'Level result.

    Per WAEC Nigeria standards, result slips contain unique WAEC identifiers.
    Checks for WAEC keywords and applicant name presence.
    """
    result = {
        'verified': False,
        'name_found': False,
        'is_waec_document': False,
        'reason': '',
        'document_type': 'WAEC'
    }

    if not text:
        result['reason'] = 'No text could be extracted from the uploaded WAEC document.'
        return result

    text_lower = text.lower()

    waec_keywords = [
        'waec', 'west african examinations council', 'ssce', 'wassce',
        'senior school certificate', 'west african senior', 'waec nigeria',
        'west africa', 'examinations council'
    ]
    result['is_waec_document'] = any(kw in text_lower for kw in waec_keywords)

    name_parts = [p.strip() for p in applicant_name.split() if len(p.strip()) > 2]
    result['name_found'] = any(part.lower() in text_lower for part in name_parts)

    if not result['is_waec_document']:
        result['reason'] = 'Document does not appear to be a valid WAEC result. Ensure you upload your WAEC SSCE/WASSCE result slip.'
    elif not result['name_found']:
        result['reason'] = 'Applicant name not found on the WAEC result. Ensure the uploaded document belongs to you.'
    else:
        result['verified'] = True
        result['reason'] = 'WAEC O\'Level result verified. Applicant name found on document.'

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  NECO O'LEVEL RESULT VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def verify_neco_document(text, applicant_name):
    """
    Validates an uploaded NECO (National Examinations Council) O'Level result.

    Per NECO Nigeria standards, result slips contain NECO-specific identifiers
    including the SSCE Internal examination branding.
    """
    result = {
        'verified': False,
        'name_found': False,
        'is_neco_document': False,
        'reason': '',
        'document_type': 'NECO'
    }

    if not text:
        result['reason'] = 'No text could be extracted from the uploaded NECO document.'
        return result

    text_lower = text.lower()

    neco_keywords = [
        'neco', 'national examinations council', 'ssce internal',
        'neco nigeria', 'national examination', 'june/july ssce',
        'neco result', 'national exams'
    ]
    result['is_neco_document'] = any(kw in text_lower for kw in neco_keywords)

    name_parts = [p.strip() for p in applicant_name.split() if len(p.strip()) > 2]
    result['name_found'] = any(part.lower() in text_lower for part in name_parts)

    if not result['is_neco_document']:
        result['reason'] = 'Document does not appear to be a valid NECO result. Ensure you upload your NECO SSCE result slip.'
    elif not result['name_found']:
        result['reason'] = 'Applicant name not found on the NECO result. Ensure the uploaded document belongs to you.'
    else:
        result['verified'] = True
        result['reason'] = 'NECO O\'Level result verified. Applicant name found on document.'

    return result
