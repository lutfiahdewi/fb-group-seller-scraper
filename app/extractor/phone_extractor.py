from __future__ import annotations
import re

# Upgraded to allow dots (\.), hyphens (\-), and spaces (\s) inside the number string
PHONE_PATTERN = re.compile(r"(?:\+62|62|08)[0-9\-\s\.]{8,18}")

def normalize_phone(phone: str) -> str:
    # Strip everything that isn't a digit
    digits = re.sub(r"\D", "", phone)
    
   # If the number starts with the country code '62', replace the '62' with '0'
    if digits.startswith("62"):
        return "0" + digits[2:]
        
    return digits

def extract_phones(text: str) -> list[str]:
    if not text:
        return []
        
    raw = PHONE_PATTERN.findall(text)
    normalized = []
    seen = set()
    
    for item in raw:
        phone = normalize_phone(item)
        
        # Indonesian numbers are typically 10 to 13 digits (excluding the country code)
        # So starting with 62, the minimum valid length is ~11.
        if len(phone) < 11 or len(phone) > 15:
            continue
            
        if phone in seen:
            continue
            
        seen.add(phone)
        normalized.append(phone)
        
    return normalized