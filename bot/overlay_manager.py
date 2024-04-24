import tkinter as tk
import pyWinhook as pyHook

from point import Point2D


class OverlayManager:
    def __init__(self):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, bg="black")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.geometry(
            f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0"
        )

    def run(self):
        self.root.mainloop()
        self.root.destroy()

    def enable_selection_mode(self, width: int = 100, height: int = 100):
        self.set_selection_size(width, height)
        self.root.attributes("-transparentcolor", "yellow")
        self.root.attributes("-alpha", 0.5)
        self.canvas.pack(fill="both", expand=True)

    def set_selection_size(self, width: int, height: int):
        self.selection_width = width
        self.selection_height = height

    def disable_selection_mode(self, selection_center: Point2D):
        self.selection_center = selection_center

        self.root.attributes("-transparentcolor", "black")
        self.root.attributes("-alpha", 1)
        self.root.wait_visibility(self.root)
        self.canvas.pack(fill="both", expand=True)

    def exit(self):
        self.root.quit()
        self.root.destroy()

    def update_selection_area(self, selection_center: Point2D):
        self.draw_selection_rect(selection_center)
        self.delete_drawing_by_tags("selection_text")

        # self.canvas.create_text(
        #     selection_center.x + self.selection_width / 2 + 10,
        #     selection_center.y - self.selection_height / 2 + 15,
        #     text=f"Left: New Label Fish",
        #     fill="white",
        #     font="Times 12",
        #     tags="selection_text",
        #     anchor="w",
        # )
        # self.canvas.create_text(
        #     selection_center.x + self.selection_width / 2 + 10,
        #     selection_center.y - self.selection_height / 2 + 35,
        #     text=f"Right: New Label No Fish",
        #     fill="white",
        #     font="Times 12",
        #     tags="selection_text",
        #     anchor="w",
        # )
        # self.canvas.create_text(
        #     selection_center.x + self.selection_width / 2 + 10,
        #     selection_center.y - self.selection_height / 2 + 55,
        #     text=f"Up: New Selection",
        #     fill="white",
        #     font="Times 12",
        #     tags="selection_text",
        #     anchor="w",
        # )
        # self.canvas.create_text(
        #     selection_center.x + self.selection_width / 2 + 10,
        #     selection_center.y - self.selection_height / 2 + 75,
        #     text=f"Down: Start Prediction",
        #     fill="white",
        #     font="Times 12",
        #     tags="selection_text",
        #     anchor="w",
        # )
        self.canvas.pack(fill="both", expand=True)

    #### REGION DRAW# ###############
    def draw_selection_rect(self, rect_center: Point2D, color: str = "red"):
        self.delete_drawing_by_tags("selection")
        x_offset = int(self.selection_width / 2)
        y_offset = int(self.selection_height / 2)
        x1 = rect_center.x - x_offset - 1
        y1 = rect_center.y - y_offset - 1
        x2 = rect_center.x + x_offset + 1
        y2 = rect_center.y + y_offset + 1
        self.draw_rectangle(x1, y1, x2, y2, color, "selection")

    def delete_drawing_by_tags(self, tags):
        self.canvas.delete(tags)

    def draw_rectangle(self, x1, y1, x2, y2, color, tags):
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline=color,
            tags=tags,
        )
        self.canvas.pack(fill="both", expand=True)

    def draw_prediction(self, value: float, trigger: bool):
        self.delete_drawing_by_tags("pred")
        self.delete_drawing_by_tags("selection")

        if trigger:
            self.draw_selection_rect(self.selection_center, "green")
        else:
            self.draw_selection_rect(self.selection_center, "red")

        self.canvas.create_text(
            self.selection_center.x,
            self.selection_center.y - self.selection_height / 2 - 15,
            text=f"Fish: {value:.2f}",
            fill="white",
            font="Times 20 bold",
            tags="pred",
        )
        # self.canvas.create_rectangle(
        #     end_s.x + 2,
        #     end_s.y + 2,
        #     end_s.x + 15,
        #     end_s.y - int(area_size * value),
        #     outline=color,
        #     fill=color,
        #     tags="pred",
        # )

        self.canvas.pack(fill="both", expand=True)
