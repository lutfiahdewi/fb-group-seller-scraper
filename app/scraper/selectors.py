GROUP_POST_CARD_SELECTORS = [
    "div[role='feed'] [aria-posinset]",
    # 2. 🆕 Buy & Sell groups: The direct child 'div' inside the main feed wall
    "div[role='feed'] > div",
    
    # 3. 🆕 Generic fallback: Facebook's standard internal class for a "Post/Card Wrapper"
    "div.x1yztbdb"
]

AUTHOR_SELECTORS = [
    "[data-ad-rendering-role='profile_name'] a[role='link']",
    "[data-ad-rendering-role='profile_name'] a[href*='/groups/'][href*='/user/']",
]

TEXT_SELECTORS = [
    "[data-ad-rendering-role='story_message'] [data-ad-comet-preview='message']",
    "[data-ad-rendering-role='story_message'] [data-ad-preview='message']",
    "[data-ad-rendering-role='story_message'] div[dir='auto']",
    # Fallbacks in case the seller only posted a Title and no description:
    "span[data-ad-rendering-role='title']", 
    "div[data-ad-rendering-role='title']",
    # 🆕 Buy & Sell post descriptions (usually lack the story_message wrapper)
    "div[data-ad-comet-preview='message']",
    "div[data-ad-preview='message']",
    
    # 🆕 Fallback to catch the main text body in product listings
    "div.xyinxu5[dir='auto']", # Common Facebook class for text blocks
]

POST_LINK_SELECTORS = [
    # 1. Standard discussion posts
    "a[href*='/groups/'][href*='/posts/']",
    
    # 2. Jual Beli (Buy & Sell) Group Listings
    "a[href*='/groups/'][href*='/permalink/']",
    "a[href*='/commerce/listing/']", # <--- 🆕 THE MISSING PIECE!
    
    # 3. Marketplace items cross-posted into the group
    "a[href*='/marketplace/item/']",
    "a[href*='sale_post_id=']",
    
    # 4. Standard fallbacks
    "a[href*='/posts/']",
    "a[href*='story_fbid=']",
    "a[href*='photo/?fbid=']",
]

TIMESTAMP_SELECTORS = [
    # 1. Targets the exact relative tracking URL used for timestamps
    "a[role='link'][href^='?__cft__']",
    
    # 2. Targets the structural accessibility wrapper (like in your snippet)
    "a[role='link']:has(span[aria-labelledby])",
    
    # 3. Legacy fallback in case they switch back
    "a[aria-label][role='link']",
]
SEE_MORE_TEXTS = [
    "See more",
    "Lihat selengkapnya",
    "Selengkapnya",
]

POST_ID_PATTERNS = [
    r"/posts/(\d+)",
    r"/permalink/(\d+)",            # Jual Beli
    r"/commerce/listing/(\d+)",     # Jual Beli
    r"sale_post_id=(\d+)",          # Cross-posts
    r"story_fbid=(\d+)",
    r"fbid=(\d+)",
]

PRODUCT_TITLE_SELECTORS = [
    "span.a8c37x1j.ni8dbmo4.stjgntxs.l9j0dhe7", # Common FB classes for large B&S titles
    "div[dir='auto'] > span > div[dir='auto']" 
]

PRODUCT_PRICE_SELECTORS = [
    "div:contains('Rp')", # Looks for IDR currency
    "span:contains('Rp')"
]