import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from image_tools import ImageModel, ImageTools


class ImageEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Image Editor (HIT137)")
        self.root.geometry("1000x650")

        self.model = ImageModel()   
        self.tools = ImageTools()      

        self.photo = None 
        self._build_menu()
        self._build_ui()
        self._bind_keys()
        self._set_status("Ready. Open an image.")

    def run(self):
        self.root.mainloop()

  
    def _build_ui(self):
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        
        left = ttk.Frame(main, padding=10)
        left.grid(row=0, column=0, sticky="ns")

        ttk.Label(left, text="Tools", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        ttk.Button(left, text="Grayscale", command=self.do_grayscale).pack(fill="x", pady=3)
        ttk.Button(left, text="Edge Detect", command=self.do_edge).pack(fill="x", pady=3)
        ttk.Button(left, text="Brightness +30", command=lambda: self.do_brightness(30)).pack(fill="x", pady=3)
        ttk.Button(left, text="Contrast x1.2", command=lambda: self.do_contrast(1.2)).pack(fill="x", pady=3)
        ttk.Button(left, text="Rotate 90°", command=self.do_rotate).pack(fill="x", pady=3)
        ttk.Button(left, text="Flip Horizontal", command=self.do_flip).pack(fill="x", pady=3)

  
        ttk.Button(left, text="Crop (Cut) Center 50%", command=self.do_crop_50).pack(fill="x", pady=3)

        ttk.Separator(left).pack(fill="x", pady=10)

   
        ttk.Label(left, text="Blur intensity (0-20)").pack(anchor="w")
        self.blur_scale = ttk.Scale(left, from_=0, to=20, orient="horizontal")
        self.blur_scale.set(0)
        self.blur_scale.pack(fill="x", pady=(0, 8))

        ttk.Button(left, text="Apply Blur", command=self.do_blur).pack(fill="x", pady=3)

        ttk.Separator(left).pack(fill="x", pady=10)

        ttk.Button(left, text="Undo (Ctrl+Z)", command=self.undo).pack(fill="x", pady=3)
        ttk.Button(left, text="Redo (Ctrl+Y)", command=self.redo).pack(fill="x", pady=3)

        self.canvas = tk.Canvas(main, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.show_image())

       
        self.status_var = tk.StringVar(value="")
        status = ttk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", side="bottom", padx=8, pady=3)

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menubar)

    def _bind_keys(self):
        self.root.bind("<Control-o>", lambda e: self.open_image())
        self.root.bind("<Control-s>", lambda e: self.save())
        self.root.bind("<Control-Shift-s>", lambda e: self.save_as())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)


    def _img_size_text(self):
        if self.model.image is None:
            return ""
        h, w = self.model.image.shape[:2]
        return f" ({w}x{h})"

    def _set_status(self, msg):
        self.status_var.set(msg + self._img_size_text())

    def _need_image(self):
        if self.model.image is None:
            messagebox.showinfo("No image", "Please open an image first.")
            return False
        return True


