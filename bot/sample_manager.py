import win32gui
import win32ui
import win32con
import traceback

from point import Point2D


class SampleCreator:
    def __init__(self):
        pass

    def capture(self, p1: Point2D, p2: Point2D):
        start = Point2D(min(p1.x, p2.x), min(p1.y, p2.y))
        end = Point2D(max(p1.x, p2.x), max(p1.y, p2.y))
        width = end.x - start.x
        height = end.y - start.y

        # grab a handle to the main desktop window
        hdesktop = win32gui.GetDesktopWindow()

        # create a device context
        desktop_dc = win32gui.GetWindowDC(hdesktop)
        img_dc = win32ui.CreateDCFromHandle(desktop_dc)

        # create a memory based device context
        mem_dc = img_dc.CreateCompatibleDC()

        # create a bitmap object
        screenshot = win32ui.CreateBitmap()
        screenshot.CreateCompatibleBitmap(img_dc, width, height)
        mem_dc.SelectObject(screenshot)

        # copy the screen into our memory device context
        mem_dc.BitBlt(
            (0, 0), (width, height), img_dc, (start.x, start.y), win32con.SRCCOPY
        )
        # save the bitmap to a file
        return (mem_dc, screenshot)

    def create_sample(self, p1: Point2D, p2: Point2D, file_path_name: str = ""):
        mem_dc, image = self.capture(p1, p2)
        image.SaveBitmapFile(mem_dc, file_path_name)

        self.clear_mem(mem_dc, image)

    def clear_mem(self, mem_dc, image):
        mem_dc.DeleteDC()
        win32gui.DeleteObject(image.GetHandle())
