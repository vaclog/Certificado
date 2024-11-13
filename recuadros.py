import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, simpledialog
import json
import os

class PDFRectangleDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Rectangle Drawer")
        
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        self.rectangles = []  # Store rectangles with names
        self.start_x = self.start_y = 0
        self.current_rect = None
        self.pdf_file = None
        self.pdf_filename = ""
        self.project_data = {"pdf_file": "", "rectangles": []}

        # Load or create a new project
        self.load_or_create_project()

    def load_or_create_project(self):
        choice = input("Do you want to load an existing project? (yes/no): ").strip().lower()
        if choice == "yes":
            project_path = filedialog.askopenfilename(filetypes=[("Project Files", "*.json")])
            if project_path and os.path.exists(project_path):
                with open(project_path, "r") as file:
                    self.project_data = json.load(file)
                self.pdf_filename = self.project_data["pdf_file"]
                if os.path.exists(self.pdf_filename):
                    self.pdf_file = fitz.open(self.pdf_filename)
                    self.show_page(0)
                    self.draw_existing_rectangles()
                else:
                    print("PDF file not found, please select a new PDF.")
                    self.load_pdf()
        else:
            self.load_pdf()

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.pdf_filename = file_path
            self.pdf_file = fitz.open(file_path)
            self.project_data["pdf_file"] = file_path
            self.show_page(0)

    def show_page(self, page_number):
        if self.pdf_file:
            page = self.pdf_file[page_number]
            pix = page.get_pixmap()
            img = tk.PhotoImage(data=pix.tobytes("ppm"))
            self.canvas.image = img  # Prevent garbage collection
            self.canvas.create_image(0, 0, image=img, anchor="nw")

    def draw_existing_rectangles(self):
        for rect_data in self.project_data["rectangles"]:
            coords = rect_data["coordinates"]
            name = rect_data["name"]
            rect = self.canvas.create_rectangle(
                coords[0][0], coords[0][1], coords[1][0], coords[1][1], outline="red"
            )
            self.canvas.create_text(
                (coords[0][0] + coords[1][0]) / 2,
                (coords[0][1] + coords[1][1]) / 2,
                text=name,
                fill="blue"
            )
            self.rectangles.append(rect_data)  # Store the rectangle info locally

    def on_mouse_down(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

    def on_mouse_drag(self, event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, current_x, current_y, outline="red"
        )

    def on_mouse_up(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        name = simpledialog.askstring("Input", "Enter a name for this rectangle:")
        if name:
            rect_data = {
                "name": name,
                "coordinates": ((self.start_x, self.start_y), (end_x, end_y))
            }
            self.rectangles.append(rect_data)
            self.project_data["rectangles"].append(rect_data)
            print(f"Rectangle '{name}' coordinates: {rect_data['coordinates']}")

            # Draw the rectangle and label on the canvas
            self.canvas.create_text(
                (self.start_x + end_x) / 2,
                (self.start_y + end_y) / 2,
                text=name,
                fill="blue"
            )

        # Save rectangles and project data to a file
        project_filename = os.path.splitext(os.path.basename(self.pdf_filename))[0] + "_project.json"
        with open(project_filename, "w") as file:
            json.dump(self.project_data, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFRectangleDrawer(root)
