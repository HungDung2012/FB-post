import json
import os
import random
import subprocess
import time

import pyautogui
import pyperclip


EDGE_PROFILE_DIRECTORY = os.environ.get("EDGE_PROFILE_DIRECTORY", "Default")
POSITIONS_PATH = os.path.join(os.path.dirname(__file__), "positions.json")

# Keep the browser fixed so click coordinates stay stable.
BROWSER_X = int(os.environ.get("FB_BROWSER_X", "0"))
BROWSER_Y = int(os.environ.get("FB_BROWSER_Y", "0"))
BROWSER_WIDTH = int(os.environ.get("FB_BROWSER_WIDTH", "1200"))
BROWSER_HEIGHT = int(os.environ.get("FB_BROWSER_HEIGHT", "900"))

# Coordinates below are absolute screen coordinates for the fixed browser window.
# Adjust these once for your screen/Facebook layout if clicks land in the wrong place.
COMPOSER_CLICK = (
    int(os.environ.get("FB_COMPOSER_X", "610")),
    int(os.environ.get("FB_COMPOSER_Y", "470")),
)
POST_BUTTON_CLICK = (
    int(os.environ.get("FB_POST_BUTTON_X", "590")),
    int(os.environ.get("FB_POST_BUTTON_Y", "722")),
)
POST_BUTTON_AFTER_IMAGE_CLICK = (
    int(os.environ.get("FB_POST_BUTTON_AFTER_IMAGE_X", "590")),
    int(os.environ.get("FB_POST_BUTTON_AFTER_IMAGE_Y", "829")),
)
PHOTO_BUTTON_CLICK = (
    int(os.environ.get("FB_PHOTO_BUTTON_X", "633")),
    int(os.environ.get("FB_PHOTO_BUTTON_Y", "648")),
)

PAGE_LOAD_SECONDS = float(os.environ.get("FB_PAGE_LOAD_SECONDS", "10"))
COMPOSER_OPEN_SECONDS = float(os.environ.get("FB_COMPOSER_OPEN_SECONDS", "3"))
BEFORE_POST_SECONDS = float(os.environ.get("FB_BEFORE_POST_SECONDS", "2"))
FILE_DIALOG_SECONDS = float(os.environ.get("FB_FILE_DIALOG_SECONDS", "2"))
IMAGE_UPLOAD_SECONDS = float(os.environ.get("FB_IMAGE_UPLOAD_SECONDS", "8"))
TYPE_DELAY_MIN = float(os.environ.get("FB_TYPE_DELAY_MIN", "0.08"))
TYPE_DELAY_MAX = float(os.environ.get("FB_TYPE_DELAY_MAX", "0.18"))

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2
POSITIONS = {}


def post_to_all(content: str, urls: list[str], log, image_paths: list[str] | None = None):
    _load_positions()
    image_paths = image_paths or []
    log("Dang dung che do auto-click tren Edge that.")
    log("Hay dung chuot len goc tren-ben-trai man hinh de dung khan cap.")
    if image_paths:
        log(f"Se dang kem {len(image_paths)} anh.")

    for i, url in enumerate(urls, 1):
        log(f"[{i}/{len(urls)}] Mo Edge: {url}")
        try:
            _post_to_url(url, content, log, image_paths)
            log("  Dang bai xong theo luong auto-click.")
        except pyautogui.FailSafeException:
            log("  Da dung khan cap vi chuot duoc dua vao goc tren-ben-trai.")
            return
        except Exception as e:
            log(f"  Loi auto-click: {e}")

        if i < len(urls):
            delay = random.uniform(8, 15)
            log(f"  Cho {delay:.1f}s truoc URL tiep theo...")
            time.sleep(delay)

    log("Hoan tat!")


def _post_to_url(url: str, content: str, log, image_paths: list[str]):
    _open_edge(url)
    log(f"Da mo Edge kich thuoc {BROWSER_WIDTH}x{BROWSER_HEIGHT} tai ({BROWSER_X}, {BROWSER_Y}).")
    log(f"Cho trang tai {PAGE_LOAD_SECONDS:.1f}s...")
    time.sleep(PAGE_LOAD_SECONDS)

    _fix_edge_window(log)
    pyautogui.press("esc")
    time.sleep(0.5)

    composer_click = _position("composer", COMPOSER_CLICK)
    log(f"Click o viet bai tai {composer_click}.")
    _human_click(*composer_click)
    time.sleep(COMPOSER_OPEN_SECONDS)

    if image_paths:
        _attach_images(image_paths, log)

    log("Nhap noi dung truc tiep vao form dang bai.")
    _type_text_slow(content)
    time.sleep(BEFORE_POST_SECONDS)

    _click_post_button(log, len(image_paths), content)
    time.sleep(3)


def _open_edge(url: str):
    subprocess.Popen(
        [
            _edge_executable(),
            "--new-window",
            f"--profile-directory={EDGE_PROFILE_DIRECTORY}",
            f"--window-position={BROWSER_X},{BROWSER_Y}",
            f"--window-size={BROWSER_WIDTH},{BROWSER_HEIGHT}",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _edge_executable() -> str:
    candidates = [
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "Microsoft", "Edge", "Application", "msedge.exe"),
    ]
    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate
    return "msedge"


def _fix_edge_window(log):
    try:
        windows = pyautogui.getWindowsWithTitle("Facebook") or pyautogui.getWindowsWithTitle("Edge")
        if not windows:
            return
        window = windows[0]
        window.activate()
        window.moveTo(BROWSER_X, BROWSER_Y)
        window.resizeTo(BROWSER_WIDTH, BROWSER_HEIGHT)
    except Exception as e:
        log(f"Khong resize duoc cua so Edge bang pyautogui, tiep tuc dung kich thuoc launch: {e}")


def _human_click(x: int, y: int):
    pyautogui.moveTo(
        x + random.randint(-3, 3),
        y + random.randint(-3, 3),
        duration=random.uniform(0.15, 0.35),
    )
    pyautogui.click()


def _attach_images(image_paths: list[str], log):
    missing_paths = [path for path in image_paths if not os.path.exists(path)]
    if missing_paths:
        raise FileNotFoundError(f"Khong tim thay file anh: {missing_paths[0]}")

    photo_button = _position("photo_button", PHOTO_BUTTON_CLICK)
    log(f"Click nut them anh tai {photo_button}.")
    _human_click(*photo_button)
    time.sleep(FILE_DIALOG_SECONDS)

    log(f"Dang chon {len(image_paths)} file anh trong hop thoai Windows.")
    pyperclip.copy(_windows_file_dialog_paths(image_paths))
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")

    log(f"Cho anh upload {IMAGE_UPLOAD_SECONDS:.1f}s...")
    time.sleep(IMAGE_UPLOAD_SECONDS)


def _click_post_button(log, image_count: int, content: str):
    image_count = min(image_count, 2)
    visual_lines = _estimate_visual_lines(content)
    post_button = _post_button_position(image_count, visual_lines)
    key = _post_button_key(image_count, visual_lines)
    log(f"Click nut Dang theo dataset {key}: {post_button}.")
    _human_click(*post_button)


def _load_positions():
    global POSITIONS
    if POSITIONS:
        return
    try:
        with open(POSITIONS_PATH, "r", encoding="utf-8") as file:
            POSITIONS = json.load(file)
    except (OSError, json.JSONDecodeError):
        POSITIONS = {}


def _position(name: str, fallback: tuple[int, int]) -> tuple[int, int]:
    value = POSITIONS.get(name)
    if isinstance(value, list) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return fallback


def _post_button_position(image_count: int, visual_lines: int) -> tuple[int, int]:
    fallback = POST_BUTTON_AFTER_IMAGE_CLICK if image_count else POST_BUTTON_CLICK
    value = POSITIONS.get("post_button", {}).get(_post_button_key(image_count, visual_lines))
    if isinstance(value, list) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return fallback


def _post_button_key(image_count: int, visual_lines: int) -> str:
    if visual_lines <= 3:
        bucket = "1_3"
    elif visual_lines <= 8:
        bucket = "4_8"
    else:
        bucket = "9_plus"
    return f"images_{image_count}_lines_{bucket}"


def _estimate_visual_lines(text: str) -> int:
    lines = 0
    for raw_line in text.splitlines() or [""]:
        line_length = max(len(raw_line), 1)
        lines += max(1, (line_length + 44) // 45)
    return lines


def _type_text_slow(text: str):
    for char in text:
        pyperclip.copy(char)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(random.uniform(TYPE_DELAY_MIN, TYPE_DELAY_MAX))


def _windows_file_dialog_paths(image_paths: list[str]) -> str:
    return " ".join(f'"{os.path.abspath(path)}"' for path in image_paths)
