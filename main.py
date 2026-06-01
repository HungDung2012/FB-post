import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from poster import post_to_all

def start_posting():
    content = txt_content.get("1.0", tk.END).strip()
    urls_raw = txt_urls.get("1.0", tk.END).strip()
    urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]

    if not content:
        messagebox.showwarning("Thiếu nội dung", "Vui lòng nhập nội dung bài đăng.")
        return
    if not urls:
        messagebox.showwarning("Thiếu URL", "Vui lòng nhập ít nhất 1 URL group/page.")
        return

    btn_post.config(state=tk.DISABLED)
    log("Bắt đầu đăng bài...")

    def run():
        post_to_all(content, urls, log)
        btn_post.config(state=tk.NORMAL)

    threading.Thread(target=run, daemon=True).start()

def log(msg):
    txt_log.config(state=tk.NORMAL)
    txt_log.insert(tk.END, msg + "\n")
    txt_log.see(tk.END)
    txt_log.config(state=tk.DISABLED)

root = tk.Tk()
root.title("FB Auto Post")
root.geometry("600x520")
root.resizable(False, False)

tk.Label(root, text="Nội dung bài đăng:").pack(anchor="w", padx=10, pady=(10, 0))
txt_content = scrolledtext.ScrolledText(root, height=6, wrap=tk.WORD)
txt_content.pack(fill=tk.X, padx=10)

tk.Label(root, text="Danh sách URL group/page (mỗi dòng 1 URL):").pack(anchor="w", padx=10, pady=(10, 0))
txt_urls = scrolledtext.ScrolledText(root, height=6, wrap=tk.WORD)
txt_urls.pack(fill=tk.X, padx=10)

btn_post = tk.Button(root, text="Đăng bài", bg="#1877f2", fg="white",
                     font=("Arial", 11, "bold"), command=start_posting)
btn_post.pack(pady=10)

tk.Label(root, text="Log:").pack(anchor="w", padx=10)
txt_log = scrolledtext.ScrolledText(root, height=8, state=tk.DISABLED, bg="#f0f0f0")
txt_log.pack(fill=tk.X, padx=10, pady=(0, 10))

root.mainloop()
