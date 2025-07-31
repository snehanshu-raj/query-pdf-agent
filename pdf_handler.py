import fitz
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

class PDFViewer:
    def __init__(self, pdf_path, page_number):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_number = page_number

        self.root = tk.Tk()
        self.root.title("PDF Viewer")
        self.root.state("zoomed")

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        self.root.focus_force()

        self.canvas = tk.Canvas(main_frame, bg="white")
        self.v_scroll = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(fill="x", side="bottom")

        self.prev_button = tk.Button(nav_frame, text="<< Previous", command=self.prev_page)
        self.next_button = tk.Button(nav_frame, text="Next >>", command=self.next_page)

        self.prev_button.pack(side="left", padx=10, pady=5)
        self.next_button.pack(side="right", padx=10, pady=5)

        self.display_page()

        self.root.mainloop()

    def render_page(self, page_number):
        page = self.doc.load_page(page_number - 1)
        pix = page.get_pixmap()
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return image

    def display_page(self):
        image = self.render_page(self.page_number)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.root.title(f"PDF Viewer - Page {self.page_number}/{len(self.doc)}")

    def next_page(self):
        if self.page_number < len(self.doc):
            self.page_number += 1
            self.display_page()
        else:
            messagebox.showinfo("End", "You're on the last page.")

    def prev_page(self):
        if self.page_number > 1:
            self.page_number -= 1
            self.display_page()
        else:
            messagebox.showinfo("Start", "You're on the first page.")

if __name__ == "__main__":
    pdf_file_path = r"C:\Users\Snehanshu Raj\OneDrive\Desktop\EAG\Assignment_4_extra\Notes\Lecture1.pdf"
    PDFViewer(pdf_file_path, 10)
