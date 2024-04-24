import zipfile
from random import randint
from PIL import Image as PILImage
from icon import Icon
from image import Image


TEMP_NAME = "temp.jpg"


class ImageArchive:
    def __init__(self, zipPath):
        self.__zipFile = zipfile.ZipFile(zipPath, "a")
        self.infoList = self.__zipFile.infolist()
        self.currentImageIndex = -1

    def addImage(self, image: Image):
        image.pImage.save(TEMP_NAME, quality=90, dpi=(72, 72))
        self.__zipFile.write(TEMP_NAME, image.fileName)

    def nextImage(self):
        self.currentImageIndex += 1
        if self.currentImageIndex >= len(self.infoList):
            return None
        file = self.infoList[self.currentImageIndex]
        pImage = PILImage.open(self.__zipFile.open(file.filename))
        return Image(pImage, file.filename)

    def getImageAmount(self):
        return len(self.infoList)

    def getRandomIcon(self):
        res = self.__getRandomImage()
        return Icon(res["image"], res["fileName"])

    def __getRandomImage(self):
        randomIndex = randint(0, len(self.infoList) - 1)
        file = self.infoList[randomIndex]
        res = {}
        res["image"] = PILImage.open(self.__zipFile.open(file.filename))
        res["fileName"] = file.filename
        return res
