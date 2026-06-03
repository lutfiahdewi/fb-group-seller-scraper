# Seller Pipeline MVP

This project implements a minimal pipeline:

1. Scrape Facebook group post cards with Playwright
2. Save raw post records to JSONL
3. Detect selling posts with rule-based logic
4. Extract Indonesian phone numbers / WhatsApp contacts
5. Save seller candidates to CSV

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

# Seller Pipeline MVP

A minimal, implementation-ready Python project scaffold for collecting Facebook group posts, storing raw records, detecting selling posts, and extracting seller phone numbers.

Facebook
   ↓
Scraper
   ↓
Raw Posts (JSON)
   ↓
Post Parser
   ↓
Selling Detector
   ↓
Phone Extractor
   ↓
Seller Records

---

## How to run
### Login 
```bash
python app/scraper/login.py
```
-### Run main app +This command will launch a Playwright browser window. You must manually log in to Facebook in this window. Once you're successfully logged in and see your Facebook feed, return to the terminal and press ENTER. The script will then save your browser session (cookies, local storage, etc.) to storage/login_session.json. This session file is crucial for the main scraper to operate without requiring manual login each time. + +Important: Ensure you complete the login process in the launched browser before pressing Enter in the terminal. A screenshot (storage/login_debug.png) will be saved to help verify the login state. + +### 2. Run the Main Scraper

### Run main app
```bash
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (...\fb-group-seller-scraper\.venv\Scripts\Activate.ps1)
python main.py
```
+This command initiates the main scraping process. It will: +- Load your saved Facebook session from login_session.json. +- Navigate to each Facebook group specified in config/groups.json. +- Scroll through the group feed to collect post cards. +- Extract raw post data. +- Apply rule-based detection to identify selling posts. +- Extract phone numbers from identified selling posts. +- Save raw post data to storage/raw_posts_<timestamp>.jsonl and seller candidates to storage/seller_candidates_<timestamp>.csv. + +If your session expires during the run, the script will detect it and prompt you to manually log in again in the browser. After re-logging in, the session will be updated. + +## Settings Configuration + +The application's behavior can be customized using environment variables defined in the .env file. A .env.example file is provided for reference; copy it to .env and modify as needed. + +Key settings include: + +- HEADLESS: (True/False, default: False)

If True, Playwright runs the browser in headless mode (without a visible browser UI). Useful for production or server environments.
If False, Playwright launches a visible browser window, which is helpful for debugging and observing the scraping process. +- SCROLL_ROUNDS: (Integer, default: 5)
Determines how many times the scraper will scroll down a group page to load more posts. Each round attempts to fetch more data. +- SCROLL_PAUSE_SECONDS: (Float, default: 2.5)
The duration in seconds the scraper waits after each scroll action. Longer pauses can help mimic human behavior and reduce the risk of detection, but will slow down the scraping process. +- POST_LIMIT_PER_GROUP: (Integer, default: 20)
The maximum number of unique posts the scraper aims to collect from each Facebook group. The scraper will stop processing a group once this limit is reached or SCROLL_ROUNDS are exhausted. +- STORAGE_DIR: (String, default: storage)
The directory where all output files (login session, raw posts, seller candidates, screenshots) will be stored. +- PLAYWRIGHT_USER_DATA_DIR: (String, default: storage/pw_fb_profile)
The directory where Playwright stores browser profile data. This is used for browser.py for persistent context, but login_session.json is the primary session file for main.py.
+## Important Considerations & Disclaimer on Facebook Data Scraping + +1.