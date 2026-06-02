import time
import random
import re
import os
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from playwright_stealth import stealth_sync

BOT_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "bot_profile")

def post_to_all(content: str, urls: list[str], log):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=BOT_PROFILE_PATH,
            channel="msedge",
            headless=False,
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
    time.sleep(random.uniform(10, 15))

    # 1. Dismiss overlay/popup: click vùng trắng + đóng dialog nếu có
    page.mouse.click(0, 0)
    time.sleep(1)
    page.keyboard.press("Escape")
    time.sleep(1)

    close_btns = page.locator('div[aria-label="Đóng"]').all()
    for btn in close_btns:
        if btn.is_visible():
            btn.click()
            time.sleep(1)

    # 2. Click ô soạn thảo
    page.goto(url, timeout=45000)
    page.wait_for_load_state("networkidle")
    time.sleep(random.uniform(5, 8))

    # 1. Tìm container cha có role="button" và chứa text mục tiêu
    # Cách này đảm bảo ta chọn đúng cái button tổng bao quanh chữ "Bạn viết gì đi..."
    composer_locator = page.locator('div[role="button"]:has(span:text("Bạn viết gì đi..."))').first
    
    # 2. Sử dụng tọa độ của phần tử này để click thay vì dùng .click() thông thường
    # Điều này tránh được các lỗi do lớp phủ (overlay) hoặc sự kiện chặn click của Facebook
    if composer_locator.is_visible():
        box = composer_locator.bounding_box()
        # Click vào tâm của button
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        log("Đã click vào ô nhập liệu dựa trên phân cấp DOM.")
    else:
        # Nếu vẫn không thấy, thử dùng CSS selector cực cụ thể cho cấu trúc bạn mô tả
        page.locator('div[role="button"] > div > span:text("Bạn viết gì đi...")').first.click(force=True)

    # 3. Đợi dialog và nhập nội dung
    page.wait_for_selector('div[role="dialog"]', timeout=20000)
    dialog = page.locator('div[role="dialog"]')

    text_input = dialog.locator('div[role="textbox"]').first
    text_input.click()
    page.keyboard.type(content, delay=150)
    time.sleep(2)

    # 4. Click nút Đăng
    post_btn = dialog.get_by_role("button", name=re.compile(r"Đăng", re.IGNORECASE)).first
    post_btn.evaluate("node => node.click()")
    log("Đã kích hoạt nút Đăng.")

    time.sleep(random.uniform(5, 8))
