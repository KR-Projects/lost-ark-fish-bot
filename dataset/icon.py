from PIL import Image as PImage
from image import Image



class Icon(Image):
    def __init__(self, pImage: PImage, fileName: str):
        if pImage.mode == "RGB":
            pImage = pImage.convert("RGBA")
        super().__init__(pImage, fileName)
        self.transparency = 1.0
        self.rotation = 0
        self.captcha = None
    
    
    def apply(self):
        self.pImage = self.pImage.resize((self.imageWidth, self.imageHeight), resample=PImage.LANCZOS)
        self.pImage = self.pImage.rotate(self.rotation, expand=1, resample=PImage.BILINEAR)
        self.__setImageTransparency(self.transparency)
        self.pImage = self.pImage.crop(self.pImage.getbbox())
        self.imageWidth = self.pImage.width
        self.imageHeight = self.pImage.height
        
    
    def copy(self):
        return Icon(self.pImage.copy(), self.fileName)
    

    def __setImageTransparency(self, transparency: float):
        newData = []
        for pixel in self.pImage.getdata():
            newPixel = (pixel[0], pixel[1], pixel[2], int(pixel[3] * transparency))
            newData.append(newPixel)
        self.pImage.putdata(newData)


def fromPath(path: str):
    parts = path.split("/")
    fileName = parts[len(parts)-1]
    return Icon(PImage.open(path), fileName)