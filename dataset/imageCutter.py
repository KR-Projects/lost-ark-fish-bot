from image import Image
import captcha
from typing import List


def cutIntoCaptchas(image: Image, width: int, height: int) -> List[captcha.Captcha]:
    captchas = []
    for tile in __cutToTiles(image, width, height):
        captchas.append(captcha.Captcha(tile.pImage, tile.fileName))
    return captchas


def __cutToTiles(image: Image, width: int, height: int) -> List[Image]:
    widthRes = __calculateOffsetAndCutCount(width, image.imageWidth)
    heightRes = __calculateOffsetAndCutCount(height, image.imageHeight)
    tiles = []
    for widthTileIndex in range(widthRes.tilesCount):
        left = widthTileIndex * width + widthRes.offset
        right = left + width
        for heightTileIndex in range(heightRes.tilesCount):
            upper = heightTileIndex * height + heightRes.offset
            lower = upper + height
            tile = Image(
                image.pImage.crop((left, upper, right, lower)),
                f"{image.name}_t{len(tiles)}.{image.extension}",
            )
            tiles.append(tile)
    return tiles


def __calculateOffsetAndCutCount(tileSize, imageSide):
    tilesCount = int(imageSide / tileSize)
    rest = imageSide % tileSize
    offset = int(rest / 2)
    return __CalcResult(tilesCount, offset)


class __CalcResult:
    def __init__(self, tilesCount, offset) -> None:
        self.tilesCount = tilesCount
        self.offset = offset
