import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from poster import post_to_all


selected_image_paths = []
IMAGE_FILETYPES = [
    ("Image files", ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif")),
    ("All files", "*.*"),
]


def start_posting():
    content = txt_content.get("1.0", tk.END).strip()
    urls_raw = txt_urls.get("1.0", tk.END).strip()
    urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]

    if not content:
        messagebox.showwarning("Thieu noi dung", "Vui long nhap noi dung bai dang.")
        return
    if not urls:
        messagebox.showwarning("Thieu URL", "Vui long nhap it nhat 1 URL group/page.")
        return

    btn_post.config(state=tk.DISABLED)
    log("Bat dau dang bai...")

    def run():
        post_to_all(content, urls, log, selected_image_paths)
        btn_post.config(state=tk.NORMAL)

    threading.Thread(target=run, daemon=True).start()


def choose_image():
    global selected_image_paths
    try:
        paths = list(filedialog.askopenfilenames(
            parent=root,
            title="Chon mot hoac nhieu anh dang kem",
            filetypes=IMAGE_FILETYPES,
        ))
    except Exception as e:
        messagebox.showerror("Loi chon anh", str(e))
        return

    if not paths:
        return

    for path in paths:
        if path not in selected_image_paths:
            selected_image_paths.append(path)
    refresh_image_list()


def clear_image():
    global selected_image_paths
    selected_image_paths = []
    refresh_image_list()


def refresh_image_list():
    lst_images.delete(0, tk.END)
    for path in selected_image_paths:
        lst_images.insert(tk.END, path)
    lbl_image.config(text=f"Da chon {len(selected_image_paths)} anh" if selected_image_paths else "Khong chon anh")


def log(msg):
    txt_log.config(state=tk.NORMAL)
    txt_log.insert(tk.END, msg + "\n")
    txt_log.see(tk.END)
    txt_log.config(state=tk.DISABLED)


root = tk.Tk()
root.title("FB Auto Post")
root.geometry("600x560")
root.resizable(False, False)

tk.Label(root, text="Noi dung bai dang:").pack(anchor="w", padx=10, pady=(10, 0))
txt_content = scrolledtext.ScrolledText(root, height=6, wrap=tk.WORD)
txt_content.pack(fill=tk.X, padx=10)

tk.Label(root, text="Danh sach URL group/page (moi dong 1 URL):").pack(anchor="w", padx=10, pady=(10, 0))
txt_urls = scrolledtext.ScrolledText(root, height=6, wrap=tk.WORD)
txt_urls.pack(fill=tk.X, padx=10)

image_frame = tk.Frame(root)
image_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
tk.Button(image_frame, text="Them anh", command=choose_image).pack(side=tk.LEFT)
tk.Button(image_frame, text="Xoa anh", command=clear_image).pack(side=tk.LEFT, padx=(6, 0))
lbl_image = tk.Label(image_frame, text="Khong chon anh", anchor="w")
lbl_image.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
lst_images = tk.Listbox(root, height=3)
lst_images.pack(fill=tk.X, padx=10, pady=(4, 0))

btn_post = tk.Button(root, text="Dang bai", bg="#1877f2", fg="white",
                     font=("Arial", 11, "bold"), command=start_posting)
btn_post.pack(pady=10)

tk.Label(root, text="Log:").pack(anchor="w", padx=10)
txt_log = scrolledtext.ScrolledText(root, height=8, state=tk.DISABLED, bg="#f0f0f0")
txt_log.pack(fill=tk.X, padx=10, pady=(0, 10))

root.mainloop()
