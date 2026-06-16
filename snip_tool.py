import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
import os
from PIL import ImageGrab, Image, ImageTk
import keyboard

SAVE_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "SnipTool")
os.makedirs(SAVE_DIR, exist_ok=True)


class SnipTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snip Tool")
        self.root.geometry("340x280")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")

        self.mode = tk.StringVar(value="freehand")
        self.custom_w = tk.StringVar(value="800")
        self.custom_h = tk.StringVar(value="600")
        self.status_var = tk.StringVar(value="Ready")
        self.last_snip_path = None

        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TRadiobutton", background="#1e1e1e", foreground="#cccccc", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff", insertcolor="#ffffff")
        style.configure("Capture.TButton", background="#0078d4", foreground="#ffffff",
                        font=("Segoe UI", 11, "bold"), padding=8)
        style.map("Capture.TButton", background=[("active", "#005fa3")])
        style.configure("Copy.TButton", background="#444", foreground="#ffffff",
                        font=("Segoe UI", 9), padding=5)
        style.map("Copy.TButton", background=[("active", "#555")])

        # Title
        tk.Label(self.root, text="✂  Snip Tool", bg="#1e1e1e", fg="#ffffff",
                 font=("Segoe UI", 13, "bold")).pack(pady=(14, 4))

        tk.Frame(self.root, bg="#333", height=1).pack(fill="x", padx=20)

        # Mode selection
        mode_frame = tk.Frame(self.root, bg="#1e1e1e")
        mode_frame.pack(pady=10)

        ttk.Radiobutton(mode_frame, text="Freehand", variable=self.mode,
                        value="freehand", command=self._toggle_fields).grid(row=0, column=0, padx=12)
        ttk.Radiobutton(mode_frame, text="Custom Size", variable=self.mode,
                        value="custom", command=self._toggle_fields).grid(row=0, column=1, padx=12)

        # Custom size inputs
        self.size_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.size_frame.pack(pady=4)

        tk.Label(self.size_frame, text="W:", bg="#1e1e1e", fg="#aaa",
                 font=("Segoe UI", 10)).grid(row=0, column=0, padx=(0, 2))
        self.w_entry = ttk.Entry(self.size_frame, textvariable=self.custom_w, width=6)
        self.w_entry.grid(row=0, column=1, padx=2)

        tk.Label(self.size_frame, text="H:", bg="#1e1e1e", fg="#aaa",
                 font=("Segoe UI", 10)).grid(row=0, column=2, padx=(8, 2))
        self.h_entry = ttk.Entry(self.size_frame, textvariable=self.custom_h, width=6)
        self.h_entry.grid(row=0, column=3, padx=2)

        tk.Label(self.size_frame, text="px", bg="#1e1e1e", fg="#666",
                 font=("Segoe UI", 9)).grid(row=0, column=4, padx=(2, 0))

        self._toggle_fields()

        # Capture button
        ttk.Button(self.root, text="▶  Capture", style="Capture.TButton",
                   command=self._start_capture).pack(pady=12, ipadx=20)

        # Copy last button
        self.copy_btn = ttk.Button(self.root, text="📋  Copy Last to Clipboard",
                                   style="Copy.TButton", command=self._copy_last)
        self.copy_btn.pack()

        # Status bar
        tk.Label(self.root, textvariable=self.status_var, bg="#111", fg="#888",
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", side="bottom", padx=0, pady=0, ipady=4)

    def _toggle_fields(self):
        state = "normal" if self.mode.get() == "custom" else "disabled"
        self.w_entry.config(state=state)
        self.h_entry.config(state=state)

    def _start_capture(self):
        self.root.withdraw()
        self.root.after(150, self._open_overlay)

    def _open_overlay(self):
        if self.mode.get() == "freehand":
            FreehandOverlay(self)
        else:
            try:
                w = int(self.custom_w.get())
                h = int(self.custom_h.get())
                if w <= 0 or h <= 0:
                    raise ValueError
            except ValueError:
                self.root.deiconify()
                messagebox.showerror("Invalid Size", "Enter valid positive integers for W and H.")
                return
            CustomSizeOverlay(self, w, h)

    def on_capture_done(self, x1, y1, x2, y2):
        self.root.deiconify()
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(SAVE_DIR, f"snip_{timestamp}.png")
            img.save(path)
            self.last_snip_path = path
            self.status_var.set(f"Saved: {os.path.basename(path)}")
            PreviewWindow(self.root, img, path)
        except Exception as e:
            self.status_var.set(f"Error: {e}")

    def on_capture_cancel(self):
        self.root.deiconify()
        self.status_var.set("Cancelled.")

    def _copy_last(self):
        if not self.last_snip_path or not os.path.exists(self.last_snip_path):
            messagebox.showinfo("No Snip", "No snip captured yet.")
            return
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-command",
                 f"Add-Type -Assembly System.Windows.Forms; "
                 f"[System.Windows.Forms.Clipboard]::SetImage("
                 f"[System.Drawing.Image]::FromFile('{self.last_snip_path}'))"],
                check=True
            )
            self.status_var.set("Copied to clipboard!")
        except Exception as e:
            self.status_var.set(f"Copy failed: {e}")


class FreehandOverlay:
    """Full-screen overlay — click and drag to select any region."""

    def __init__(self, app):
        self.app = app
        self.start_x = self.start_y = 0
        self.rect = None

        self.win = tk.Toplevel()
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.25)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.win.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.win.bind("<Escape>", lambda e: self._cancel())

        label = tk.Label(self.win, text="Drag to select  |  ESC to cancel",
                         bg="black", fg="white", font=("Segoe UI", 11))
        label.place(relx=0.5, rely=0.02, anchor="n")

    def _on_press(self, e):
        self.start_x, self.start_y = e.x, e.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(e.x, e.y, e.x, e.y,
                                                  outline="#0078d4", width=2)

    def _on_drag(self, e):
        self.canvas.coords(self.rect, self.start_x, self.start_y, e.x, e.y)

    def _on_release(self, e):
        x1, y1 = min(self.start_x, e.x), min(self.start_y, e.y)
        x2, y2 = max(self.start_x, e.x), max(self.start_y, e.y)
        self.win.destroy()
        if x2 - x1 > 4 and y2 - y1 > 4:
            self.app.on_capture_done(x1, y1, x2, y2)
        else:
            self.app.on_capture_cancel()

    def _cancel(self):
        self.win.destroy()
        self.app.on_capture_cancel()


class CustomSizeOverlay:
    """Full-screen overlay — click once to anchor a fixed-size rectangle."""

    def __init__(self, app, w, h):
        self.app = app
        self.w = w
        self.h = h
        self.rect = None

        self.win = tk.Toplevel()
        self.win.attributes("-fullscreen", True)
        self.win.attributes("-alpha", 0.25)
        self.win.attributes("-topmost", True)
        self.win.configure(bg="black")
        self.win.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Motion>", self._on_move)
        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.win.bind("<Escape>", lambda e: self._cancel())

        label = tk.Label(self.win, text=f"Click to capture  {w}×{h}px  |  ESC to cancel",
                         bg="black", fg="white", font=("Segoe UI", 11))
        label.place(relx=0.5, rely=0.02, anchor="n")

    def _on_move(self, e):
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            e.x, e.y, e.x + self.w, e.y + self.h,
            outline="#0078d4", width=2
        )

    def _on_click(self, e):
        x1, y1 = e.x, e.y
        x2, y2 = x1 + self.w, y1 + self.h
        self.win.destroy()
        self.app.on_capture_done(x1, y1, x2, y2)

    def _cancel(self):
        self.win.destroy()
        self.app.on_capture_cancel()


class PreviewWindow:
    """Shows the captured snip with Save/Copy options."""

    def __init__(self, parent, img, path):
        self.img = img
        self.path = path

        win = tk.Toplevel(parent)
        win.title("Snip Preview")
        win.configure(bg="#1e1e1e")
        win.attributes("-topmost", True)

        # Resize for preview (max 600×400)
        pw, ph = img.size
        scale = min(600 / pw, 400 / ph, 1.0)
        preview = img.resize((int(pw * scale), int(ph * scale)), Image.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(preview)

        tk.Label(win, image=self.tk_img, bg="#1e1e1e").pack(padx=10, pady=10)

        info = f"{pw}×{ph}px  —  {os.path.basename(path)}"
        tk.Label(win, text=info, bg="#1e1e1e", fg="#888",
                 font=("Segoe UI", 9)).pack()

        btn_frame = tk.Frame(win, bg="#1e1e1e")
        btn_frame.pack(pady=8)

        tk.Button(btn_frame, text="📂 Open Folder", bg="#333", fg="white",
                  font=("Segoe UI", 9), relief="flat", padx=10,
                  command=self._open_folder).pack(side="left", padx=5)

        tk.Button(btn_frame, text="📋 Copy", bg="#0078d4", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", padx=10,
                  command=self._copy).pack(side="left", padx=5)

        tk.Button(btn_frame, text="✖ Close", bg="#444", fg="white",
                  font=("Segoe UI", 9), relief="flat", padx=10,
                  command=win.destroy).pack(side="left", padx=5)

    def _open_folder(self):
        os.startfile(os.path.dirname(self.path))

    def _copy(self):
        try:
            import subprocess
            subprocess.run(
                ["powershell", "-command",
                 f"Add-Type -Assembly System.Windows.Forms; "
                 f"[System.Windows.Forms.Clipboard]::SetImage("
                 f"[System.Drawing.Image]::FromFile('{self.path}'))"],
                check=True
            )
        except Exception as e:
            messagebox.showerror("Copy Failed", str(e))


if __name__ == "__main__":
    SnipTool()
