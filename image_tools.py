import cv2
import numpy as np


class ImageModel:
    def __init__(self):
        self.image = None         
        self.original = None       
        self.path = None
        self.undo_stack = []
        self.redo_stack = []
        self.dirty = False

    def load(self, img, path):
        self.image = img
        self.original = img.copy()
        self.path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.dirty = False

    def push(self):
        if self.image is not None:
            self.undo_stack.append(self.image.copy())
            self.redo_stack.clear()

    def set_image(self, img):
        self.image = img
        self.dirty = True

    def undo(self):
        if self.image is None or not self.undo_stack:
            return False
        self.redo_stack.append(self.image.copy())
        self.image = self.undo_stack.pop()
        self.dirty = True
        return True

    def redo(self):
        if self.image is None or not self.redo_stack:
            return False
        self.undo_stack.append(self.image.copy())
        self.image = self.redo_stack.pop()
        self.dirty = True
        return True


class ImageTools:

    @staticmethod
    def grayscale(img):
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def blur(img, intensity):
        # intensity 0..20 -> kernel odd size
        k = max(1, int(intensity))
        k = 2 * k + 1
        return cv2.GaussianBlur(img, (k, k), 0)

    @staticmethod
    def edge(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 60, 160)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def brightness(img, beta):
        # beta = +30 for brighter
        return cv2.convertScaleAbs(img, alpha=1.0, beta=int(beta))

    @staticmethod
    def contrast(img, alpha):
        # alpha = 1.2 for higher contrast
        return cv2.convertScaleAbs(img, alpha=float(alpha), beta=0)

    @staticmethod
    def rotate90(img):
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    @staticmethod
    def flip_h(img):
        return cv2.flip(img, 1)

    @staticmethod
    def crop_center_percent(img, percent=50):
        h, w = img.shape[:2]
        p = max(10, min(90, int(percent))) / 100.0  

        new_w = max(1, int(w * p))
        new_h = max(1, int(h * p))

        x1 = (w - new_w) // 2
        y1 = (h - new_h) // 2
        x2 = x1 + new_w
        y2 = y1 + new_h

        return img[y1:y2, x1:x2].copy()



    def _apply(self, func, msg):
        if not self._need_image():
            return
        try:
            self.model.push()
            out = func(self.model.image)
            self.model.set_image(out)
            self.show_image()
            self._set_status(msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def open_image(self):
        if self.model.dirty:
            ok = messagebox.askyesno("Unsaved changes", "You have unsaved changes. Continue opening?")
            if not ok:
                return

        path = filedialog.askopenfilename(
            title="Open image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return

        img = cv2.imread(path)
        if img is None:
            messagebox.showerror("Open error", "Could not open this image.")
            return

        self.model.load(img, path)
        self.show_image()
        self._set_status("Opened")

    def save(self):
        if not self._need_image():
            return
        if not self.model.path:
            self.save_as()
            return
        self._save_to(self.model.path)

    def save_as(self):
        if not self._need_image():
            return
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".png",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        if not path:
            return
        self._save_to(path)



