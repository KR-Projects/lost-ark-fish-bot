from PIL import Image as PImage


class Image:
    def __init__(self, pImage: PImage, fileName: str):
        self.fileName = fileName
        nameParts = fileName.split('.')
        self.name = nameParts[0]
        self.extension = nameParts[1]
        self.pImage = pImage
        self.__originalImageWidth = pImage.width
        self.__originalImageHeight = pImage.height
        self.imageWidth = self.__originalImageWidth
        self.imageHeight = self.__originalImageHeight


    def copy(self):
        return Image(self.pImage.copy(), self.fileName)


def fromPath(path: str):
    parts = path.split("/")
    fileName = parts[len(parts)-1]
    return Image(PImage.open(path), fileName)