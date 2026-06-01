import time
import random
import os
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import stealth_sync

EDGE_USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")

def post_to_all(content: str, urls: list[str], log):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=EDGE_USER_DATA,
            channel="msedge",
            headless=False,
            args=["--profile-directory=Default"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        stealth_sync(page)

        log("Đang mở Facebook...")
        page.goto("https://www.facebook.com/", timeout=30000)
        page.wait_for_load_state("domcontentloaded")

        if "login" in page.url or page.locator('[data-testid="royal_login_button"]').count() > 0:
            log("Chưa đăng nhập. Vui lòng đăng nhập trong cửa sổ (tối đa 90s)...")
            try:
                page.wait_for_function(
                    "() => !window.location.href.includes('login')",
                    timeout=90000
                )
            except PWTimeout:
                log("Hết thời gian chờ đăng nhập.")
                browser.close()
                return

        log("Đã đăng nhập. Bắt đầu đăng bài...")

        for i, url in enumerate(urls, 1):
            log(f"[{i}/{len(urls)}] Đang xử lý: {url}")
            try:
                _post_to_url(page, url, content, log)
                log(f"  ✓ Đăng thành công")
            except Exception as e:
                page.screenshot(path=f"error_{i}.png")
                log(f"  ✗ Lỗi: {e} (đã lưu ảnh error_{i}.png)")
            if i < len(urls):
                delay = random.uniform(5, 15)
                log(f"  Chờ {delay:.1f}s...")
                time.sleep(delay)

        browser.close()
        log("Hoàn tất!")

def _post_to_url(page, url: str, content: str, log):
    page.goto(url, timeout=45000)
    page.wait_for_load_state("networkidle")
    time.sleep(random.uniform(5, 8))

    # Bước 1: Click ô soạn thảo bằng text hiển thị (ổn định nhất)
    composer = page.get_by_text("Bạn viết gì đi...")
    if not composer.is_visible():
        composer = page.locator('div[role="button"]:has-text("Bạn viết gì đi...")').first
    composer.click()

    # Bước 2: Đợi dialog xuất hiện
    page.wait_for_selector('div[role="dialog"]', timeout=15000)
    dialog = page.locator('div[role="dialog"]')

    # Bước 3: Nhập nội dung vào contenteditable trong dialog
    text_input = dialog.locator('div[contenteditable="true"]').first
    text_input.click()
    page.keyboard.type(content, delay=100)
    time.sleep(2)

    # Bước 4: Click nút Đăng
    post_btn = dialog.get_by_role("button", name="Đăng")
    if post_btn.is_visible():
        post_btn.click()
        log("Đã nhấn Đăng.")
    else:
        dialog.locator('button[type="submit"]').click()
        log("Đã nhấn Đăng (submit).")

    time.sleep(random.uniform(5, 8))
