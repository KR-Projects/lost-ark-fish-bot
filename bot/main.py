import pyWinhook as pyHook
import threading
import pythoncom
import datetime
import pyWinhook as pyHook
import os
import time
import random


from tensorflow import keras
from PIL import Image
from keras.models import Model
import numpy as np

from overlay_manager import OverlayManager
from sample_manager import SampleCreator
from point import Point2D

import win32gui
import win32con
import win32api


class App:
    def __init__(self):
        self.area_heigt = 200
        self.area_width = 100
        self.enable_prediction = False
        self.overlay_manager = OverlayManager()
        self.sample_creator = SampleCreator()
        self.selection_enabled = True
        self.selection_point = Point2D(0, 0)
        self.is_fishing = False
        self.model: keras.Model

        self.overlay_manager.enable_selection_mode(self.area_width, self.area_heigt)

        self.current_file_path = os.path.dirname(os.path.abspath(__file__))

        self.__create_dir(os.path.join(self.current_file_path, "sampels"))
        self.__create_dir(os.path.join(self.current_file_path, "sampels", "fish"))
        self.__create_dir(os.path.join(self.current_file_path, "sampels", "no_fish"))

        print(os.path.join(self.current_file_path, "fish_model"))

        self.model: keras.Model = keras.models.load_model(
            os.path.join(self.current_file_path, "fish_model")
        )

    def __create_dir(self, path: str):
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"Ordner '{path}' wurde erstellt.")
        else:
            print(f"Der Ordner '{path}' existiert bereits.")

    def get_capture_start_point(self):
        x = self.selection_point.x - int(self.area_width / 2)
        y = self.selection_point.y - int(self.area_heigt / 2)
        return Point2D(x, y)

    def get_capture_end_point(self):
        x = self.selection_point.x + int(self.area_width / 2)
        y = self.selection_point.y + int(self.area_heigt / 2)
        return Point2D(x, y)

    def get_time_as_str(self):
        now = datetime.datetime.now()
        dateiformat = "%Y-%m-%d_%H-%M-%S-%f"
        return now.strftime(dateiformat)

    def run(self):
        self.overlay_manager.run()

    def on_mouse_down(self, event: pyHook.MouseEvent):
        if self.selection_enabled:
            self.selection_enabled = False
            self.selection_point = Point2D(*event.Position)
            self.overlay_manager.disable_selection_mode(self.selection_point)
        return True

    def on_mouse_move(self, event: pyHook.MouseEvent):
        if self.selection_enabled:
            self.overlay_manager.update_selection_area(Point2D(*event.Position))
        return True

    def on_key_down(self, event: pyHook.KeyboardEvent):
        if event.Key == "Escape":
            self.overlay_manager.exit()
            quit()
        elif event.Key == "Up":
            if self.enable_prediction:
                print("Disable Predictor first")
                return True

            self.selection_enabled = True
            self.overlay_manager.enable_selection_mode(self.area_width, self.area_heigt)
        elif event.Key == "Down":
            if self.selection_enabled:
                print("Select Area first!")
                return True

            if self.enable_prediction:
                self.enable_prediction = False
            else:
                self.enable_prediction = True
                self.predict_thread = threading.Thread(target=self.predict, daemon=True)
                self.predict_thread.start()

        elif event.Key == "Left":
            self.sample_creator.create_sample(
                self.get_capture_start_point(),
                self.get_capture_end_point(),
                file_path_name=os.path.join(
                    self.current_file_path,
                    "sampels",
                    "fish",
                    f"{self.get_time_as_str()}.bmp",
                ),
            )
        elif event.Key == "Right":
            self.sample_creator.create_sample(
                self.get_capture_start_point(),
                self.get_capture_end_point(),
                file_path_name=os.path.join(
                    self.current_file_path,
                    "sampels",
                    "no_fish",
                    f"{self.get_time_as_str()}.bmp",
                ),
            )
        return True

    def get_activations(self, layer_name, input_data):
        activation_model = Model(
            inputs=self.model.input, outputs=self.model.get_layer(layer_name).output
        )
        activations = activation_model.predict(input_data)
        return activations

    def generate_heatmap(self, activations):
        heatmap = np.mean(activations, axis=-1)
        return heatmap[0]

    def predict(self):
        while self.enable_prediction:
            mem_dc, screenshot = self.sample_creator.capture(
                self.get_capture_start_point(), self.get_capture_end_point()
            )
            bmpinfo = screenshot.GetInfo()
            im = Image.frombuffer(
                "RGB",
                (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                screenshot.GetBitmapBits(True),
                "raw",
                "BGRX",
                0,
                1,
            )
            self.sample_creator.clear_mem(mem_dc, screenshot)
            image_array = np.array(im).reshape(1, 200, 100, 3)
            fish_activation = self.model.predict(image_array, verbose=0)[0]

            if fish_activation > 0.5:
                # fish
                self.overlay_manager.draw_selection_rect(self.selection_point, "green")

                def callback(handle, param):
                    s = win32gui.GetClassName(handle)
                    try:
                        vkc = win32api.VkKeyScan("e")
                        win32gui.PostMessage(handle, win32con.WM_KEYDOWN, vkc, 0)
                    except Exception:
                        pass

                window_id = win32gui.FindWindow(None, "LOSTARK Client")

                win32gui.EnumChildWindows(window_id, callback, 0)
                time.sleep(random.uniform(6, 10))
                win32gui.EnumChildWindows(window_id, callback, 0)

            else:
                # no fish
                self.overlay_manager.draw_selection_rect(self.selection_point, "blue")
        self.overlay_manager.draw_selection_rect(self.selection_point, "red")

    def pull_fish(self):
        pass


if __name__ == "__main__":
    app = App()

    # create the hook mananger
    hm = pyHook.HookManager()
    # register two callbacks
    hm.MouseLeftDown = app.on_mouse_down
    hm.MouseMove = app.on_mouse_move
    hm.KeyDown = app.on_key_down

    # hook into the mouse and keyboard events
    hm.HookMouse()
    hm.HookKeyboard()

    hotkey_thread = threading.Thread(target=pythoncom.PumpMessages)
    hotkey_thread.daemon = True
    hotkey_thread.start()

    app.run()

    hm.UnhookKeyboard()
    hm.UnhookMouse()
