import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from poster import post_to_all


selected_image_path = ""


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
        post_to_all(content, urls, log, selected_image_path or None)
        btn_post.config(state=tk.NORMAL)

    threading.Thread(target=run, daemon=True).start()


def choose_image():
    global selected_image_path
    selected_image_path = filedialog.askopenfilename(
        title="Chon anh dang kem",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.webp *.gif"),
            ("All files", "*.*"),
        ],
    )
    if selected_image_path:
        lbl_image.config(text=selected_image_path)


def clear_image():
    global selected_image_path
    selected_image_path = ""
    lbl_image.config(text="Khong chon anh")


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
tk.Button(image_frame, text="Chon anh", command=choose_image).pack(side=tk.LEFT)
tk.Button(image_frame, text="Xoa anh", command=clear_image).pack(side=tk.LEFT, padx=(6, 0))
lbl_image = tk.Label(image_frame, text="Khong chon anh", anchor="w")
lbl_image.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)

btn_post = tk.Button(root, text="Dang bai", bg="#1877f2", fg="white",
                     font=("Arial", 11, "bold"), command=start_posting)
btn_post.pack(pady=10)

tk.Label(root, text="Log:").pack(anchor="w", padx=10)
txt_log = scrolledtext.ScrolledText(root, height=8, state=tk.DISABLED, bg="#f0f0f0")
txt_log.pack(fill=tk.X, padx=10, pady=(0, 10))

root.mainloop()
