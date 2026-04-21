from __future__ import annotations
import re

# Expanded with heavy local social commerce slang
PRODUCT_KEYWORDS = [
    # Standard
    "jual", "ready", "ready stok", "open order", "preorder", "po",
    "cod", "promo", "diskon", "harga", "order",
    # Local Slang & Abbreviations
    "japri", "dm", "inbox", "mahar", "nego", "minat", "lokasi", "lok", 
    "pc", "wa", "rekber", "murmer", "cuan", "sold", "tt", "bt", 
    "tukar tambah", "barter", "dijual", "lepas", "angkut",
    r"\bdijual\b", r"\bready\b", r"\bmurah\b", r"\bpromo\b", r"harga"
]
SERVICE_KEYWORDS = [
    r"\bojek\b", r"antar jemput", r"\bkurir\b", r"\bjasa\b", r"\bpijat\b", r"\burut\b"
    # ... add the rest from the list above ...
]
# Combine them into one master list for the scraper to check
ALL_SELLING_KEYWORDS = PRODUCT_KEYWORDS + SERVICE_KEYWORDS

QUESTION_PATTERNS = [
    r"ada yang jual",
    r"siapa yang jual",
    r"where to buy",
    r"info jualan",
    r"info lapak"
]

# Upgraded to catch "50k", "50rb", "50 rb", "50ribu"
PRICE_PATTERN = re.compile(
    # 1. Matches formal prices: Rp 15000, Rp 1.500.000
    r"(?:rp\s?\d+(?:[\.,]\d+)*)"                       
    
    # 2. Matches decimals + multipliers: 1,5jt, 1.5 jt, 50k, 7 juta
    r"|(?:\d+(?:[\.,]\d+)?\s*(?:k|rb|ribu|jt|juta)\b)" 
    
    # 3. Matches standard formatted numbers: 1.500.000, 50.000 (must have a dot/comma)
    r"|(?:\d{1,3}(?:[\.,]\d{3})+)"                     
    
    # 4. Matches spelled-out prices: "satu juta", "setengah juta", "lima ribu"
    r"|(?:satu|dua|tiga|empat|lima|enam|tujuh|delapan|sembilan|sepuluh|sebelas|setengah)\s+(?:juta|ribu)\b", 
    
    re.IGNORECASE
)

def normalize_text(text: str) -> str:
    # Lowercase and remove extra whitespaces
    return re.sub(r"\s+", " ", text.lower()).strip()

def is_likely_question(text: str) -> bool:
    normalized = normalize_text(text)
    return any(re.search(pattern, normalized) for pattern in QUESTION_PATTERNS)

def has_selling_keyword(text: str) -> bool:
    normalized = normalize_text(text)
    # Using regex word boundaries (\b) so "batal" doesn't trigger "bt" (barter)
    for keyword in ALL_SELLING_KEYWORDS:
        if re.search(rf"\b{keyword}\b", normalized):
            return True
    return False

def has_price_signal(text: str) -> bool:
    return bool(PRICE_PATTERN.search(text.lower()))

def is_selling_post(text: str) -> bool:
    if not text:
        return False
        
    if is_likely_question(text):
        return False # It's a buyer asking, not a seller selling

    # It's a selling post if it has BOTH a keyword and a price, 
    # OR if it just has a very strong selling keyword.
    if has_selling_keyword(text) or has_price_signal(text):
        return True
        
    return False