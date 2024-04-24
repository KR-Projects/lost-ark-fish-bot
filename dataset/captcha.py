from PIL import Image as PImage
from random import randint
from image import Image
from icon import Icon
import debug
from typing import List


class _Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class _IconPlacement:
    def __init__(self, icon: Icon) -> None:
        self.icon = icon
        self.position = _Position(0, 0)
        self.fullPixel = self.icon.imageWidth * self.icon.imageHeight
        self.coveredPixel = 0

    def calcPossibleOffset(self, side, minVisibility):
        if side == 0:
            return 0
        protectedPixel = int(self.fullPixel * minVisibility)
        canBeUsedPixel = self.fullPixel - protectedPixel
        if self.coveredPixel >= canBeUsedPixel:
            return 0
        openPixel = canBeUsedPixel - self.coveredPixel
        offset = int(openPixel / side)
        return offset

    def apply(self, width, height):
        self.coveredPixel += width * height
        if self.coveredPixel > self.fullPixel:
            debug.debugLine("visibility under 0...set to 0")
            self.coveredPixel = self.fullPixel


class _Range:
    def __init__(
        self,
        min: int,
        max: int,
        beforePlacement: _IconPlacement,
        beforeOverlapWidth: int,
        afterPlacement: _IconPlacement,
        afterOverlapWidth: int,
    ) -> None:
        self.min = int(min)
        self.max = int(max)
        self.beforePlacement = beforePlacement
        self.beforeOverlapWidth = beforeOverlapWidth
        self.afterPlacement = afterPlacement
        self.afterOverlapWidth = afterOverlapWidth


class Captcha(Image):
    def __init__(self, pImage: PImage, fileName: str):
        super().__init__(pImage, fileName)
        self.iconPlacements = []
        self.hasDoubleIcons = False

    def addIconsRandom(self, newIcons: List[Icon], minVisibilty: int):
        allDone = False
        while not allDone:
            allDone = True
            self.iconPlacements.clear()
            for icon in newIcons:
                gotAPlace = False
                tries = 0
                while not gotAPlace:
                    tries += 1
                    newPlace = _IconPlacement(icon)
                    offset = newPlace.calcPossibleOffset(
                        newPlace.icon.imageHeight, minVisibilty
                    )
                    newPlace.position.x = randint(
                        0 - offset, self.imageWidth - newPlace.icon.imageWidth + offset
                    )
                    debug.debugLine(f"use x: {newPlace.position.x}")
                    offPlace = newPlace.position.x
                    if (
                        newPlace.position.x + newPlace.icon.imageWidth
                    ) > self.imageWidth:
                        offPlace = self.imageWidth - (
                            newPlace.position.x + newPlace.icon.imageWidth
                        )
                    if offPlace < 0:
                        offPlace *= -1
                        debug.debugLine("apply x offplace")
                        newPlace.apply(offPlace, newPlace.icon.imageHeight)
                    if not self.setY(newPlace, minVisibilty):
                        if tries >= 100:
                            break
                        continue
                    self.iconPlacements.append(newPlace)
                    # self.save("temp.jpg")
                    debug.debugLine("-next icon/next try-")
                    gotAPlace = True
                if tries >= 100 and not gotAPlace:
                    allDone = False
                    break
        self.__pasteIcons()
        if debug.DEBUG:
            for place in self.iconPlacements:
                self.debugPlace(place)

    def __pasteIcons(self):
        for placement in self.iconPlacements:
            self.__pasteIcon(placement)

    def __pasteIcon(self, place: _IconPlacement):
        self.pImage.paste(
            place.icon.pImage, (place.position.x, place.position.y), place.icon.pImage
        )

    def debugPlace(self, place: _IconPlacement):
        debug.debugLine("==")
        debug.debugLine(f"coveredPixel: {place.coveredPixel}")
        debug.debugLine(f"fullPixel: {place.fullPixel}")
        debug.debugLine(f"position.x: {place.position.x}")
        debug.debugLine(f"position.y: {place.position.y}")
        debug.debugLine(f"icon.imageWidth: {place.icon.imageWidth}")
        debug.debugLine(f"icon.imageHeight: {place.icon.imageHeight}")
        debug.debugLine("==")

    def setY(self, newPlace: _IconPlacement, minVisibilty: int):
        ranges = self.getRanges(newPlace, minVisibilty)
        if len(ranges) <= 0:
            return False
        debug.debugLine("got ranges:")
        i = 0
        for range in ranges:
            debug.debugLine(f"--{i}")
            debug.debugLine(f"range.min: {range.min}")
            debug.debugLine(f"range.max: {range.max}")
            debug.debugLine(f"range.beforePlacement: {range.beforePlacement}")
            debug.debugLine(f"range.beforeOverlapWidth: {range.beforeOverlapWidth}")
            debug.debugLine(f"range.afterPlacement: {range.afterPlacement}")
            debug.debugLine(f"range.afterOverlapWidth: {range.afterOverlapWidth}")
            debug.debugLine("--")
            i += 1
        randIndex = randint(0, len(ranges) - 1)
        usedRange = ranges[randIndex]
        debug.debugLine(f"use range: {randIndex}")
        self.applyRange(usedRange, newPlace)
        return True

    def applyRange(self, usedRange: _Range, newPlace: _IconPlacement):
        y = randint(usedRange.min, usedRange.max)
        debug.debugLine(f"use y: {y}")
        beforePlacement = usedRange.beforePlacement
        beforeCutOff = y
        if beforePlacement is not None:
            beforeCutOff = y - (
                beforePlacement.position.y + beforePlacement.icon.imageHeight
            )
        if beforeCutOff < 0:
            beforeCutOff *= -1
            debug.debugLine(f"has beforeCutOff {beforeCutOff}")
            debug.debugLine(f"apply to newPlace")
            newPlace.apply(usedRange.beforeOverlapWidth, beforeCutOff)
            if beforePlacement is not None:
                debug.debugLine(f"apply to beforePlacement")
                beforePlacement.apply(usedRange.beforeOverlapWidth, beforeCutOff)

        afterPlacement = usedRange.afterPlacement
        afterCutOff = self.imageHeight - (y + newPlace.icon.imageHeight)
        if afterPlacement is not None:
            afterCutOff = afterPlacement.position.y - (y + newPlace.icon.imageHeight)
        if afterCutOff < 0:
            afterCutOff *= -1
            debug.debugLine(f"has afterCutOff {afterCutOff}")
            debug.debugLine(f"apply to newPlace")
            newPlace.apply(usedRange.afterOverlapWidth, afterCutOff)
            if afterPlacement is not None:
                debug.debugLine(f"apply to afterPlacement")
                afterPlacement.apply(usedRange.afterOverlapWidth, afterCutOff)

        newPlace.position.y = y

    def getRanges(self, newPlace: _IconPlacement, minVisibilty: int):
        debug.debugLine("getting ranges...")
        sortedPlacements = self.getIconsInRangeSorted(
            newPlace.position.x, newPlace.position.x + newPlace.icon.imageWidth
        )
        debug.debugLine(f"got {len(sortedPlacements)} sortedPlacements")
        for sPlacement in sortedPlacements:
            self.debugPlace(sPlacement)
        possibleRanges = len(sortedPlacements) + 1
        ranges = []
        if possibleRanges == 1:
            debug.debugLine(
                f"no sorted placements so only the image borders himself..."
            )
            offset = newPlace.calcPossibleOffset(newPlace.icon.imageWidth, minVisibilty)
            ranges.append(
                _Range(
                    0 - offset,
                    self.imageHeight - newPlace.icon.imageHeight + offset,
                    None,
                    newPlace.icon.imageWidth,
                    None,
                    newPlace.icon.imageWidth,
                )
            )
        else:
            debug.debugLine(f"have sortedplacements so i check every")
            lastPlacement = None
            for sortedPlacement in sortedPlacements:
                range = self.getRange(
                    newPlace, minVisibilty, sortedPlacement, lastPlacement
                )
                if range is not None:
                    ranges.append(range)
                lastPlacement = sortedPlacement
            range = self.getRange(newPlace, minVisibilty, None, lastPlacement)
            if range is not None:
                ranges.append(range)
        return ranges

    def getRange(
        self,
        newPlace: _IconPlacement,
        minVisibilty: int,
        sortedPlacement: _IconPlacement,
        lastPlacement: _IconPlacement,
    ):
        debug.debugLine("get range")
        rangeStart = 0
        beforeOverlap = 0
        upperEdge = 0
        if lastPlacement is None:
            debug.debugLine(
                f"no before placement so i calc with full image widht / crash into image border"
            )
            rangeStart = (
                newPlace.calcPossibleOffset(newPlace.icon.imageWidth, minVisibilty) * -1
            )
            rangeStart = int(rangeStart)
            beforeOverlap = newPlace.icon.imageWidth
        else:
            debug.debugLine(f"have before placement")
            if (
                lastPlacement.position.y + lastPlacement.icon.imageHeight
                >= self.imageHeight
            ):
                debug.debugLine(f"before icon is out of image. returning none")
                return None
            if newPlace.position.x > lastPlacement.position.x:
                beforeOverlap = (
                    lastPlacement.position.x + lastPlacement.icon.imageWidth
                ) - newPlace.position.x
            else:
                beforeOverlap = (
                    newPlace.position.x + newPlace.icon.imageWidth
                ) - lastPlacement.position.x
            debug.debugLine(f"beforeOverlap: {beforeOverlap}")
            rangeStart = min(
                newPlace.calcPossibleOffset(beforeOverlap, minVisibilty),
                lastPlacement.calcPossibleOffset(beforeOverlap, minVisibilty),
            )
            debug.debugLine(f"rangeStart: {rangeStart}")
            rangeStart = int(rangeStart)
            debug.debugLine(f"rangeStart as int: {rangeStart}")
            rangeStart = (
                lastPlacement.position.y + lastPlacement.icon.imageHeight
            ) - rangeStart
            debug.debugLine(f"rangeStart: {rangeStart}")
            if rangeStart < lastPlacement.position.y:
                debug.debugLine(f"rangestart above y of before placement")
                rangeStart = lastPlacement.position.y
                debug.debugLine(f"rangeStart: {rangeStart}")
            upperEdge = lastPlacement.position.y + lastPlacement.icon.imageHeight

        rangeEnd = 0
        afterOverlap = 0
        lowerEdge = self.imageHeight
        if sortedPlacement is None:
            debug.debugLine(
                f"no after placement so i calc with full image widht / crash into image border"
            )
            rangeEnd = (
                self.imageHeight - newPlace.icon.imageHeight
            ) + newPlace.calcPossibleOffset(newPlace.icon.imageWidth, minVisibilty)
            rangeEnd = int(rangeEnd)
            afterOverlap = newPlace.icon.imageWidth
        else:
            debug.debugLine(f"have after placement")
            if sortedPlacement.position.y <= 0:
                debug.debugLine(f"before icon is out of image. returning none")
                return None
            if newPlace.position.x > sortedPlacement.position.x:
                afterOverlap = (
                    sortedPlacement.position.x + sortedPlacement.icon.imageWidth
                ) - newPlace.position.x
            else:
                afterOverlap = (
                    newPlace.position.x + newPlace.icon.imageWidth
                ) - sortedPlacement.position.x
            debug.debugLine(f"afterOverlap: {afterOverlap}")
            rangeEnd = min(
                newPlace.calcPossibleOffset(afterOverlap, minVisibilty),
                sortedPlacement.calcPossibleOffset(afterOverlap, minVisibilty),
            )
            debug.debugLine(f"rangeEnd: {rangeEnd}")
            rangeEnd = int(rangeEnd)
            debug.debugLine(f"rangeEnd as int: {rangeEnd}")
            rangeEnd = (
                sortedPlacement.position.y - newPlace.icon.imageHeight
            ) + rangeEnd
            debug.debugLine(f"rangeEnd: {rangeEnd}")
            if rangeEnd > sortedPlacement.position.y:
                debug.debugLine(f"rangeEnd under y of after placement")
                rangeEnd = sortedPlacement.position.y
                debug.debugLine(f"rangeEnd: {rangeEnd}")
            lowerEdge = sortedPlacement.position.y
        if (lowerEdge - upperEdge) < newPlace.icon.imageHeight:
            debug.debugLine(f"clean space isnt enough. returning none")
            return None
        return _Range(
            rangeStart,
            rangeEnd,
            lastPlacement,
            beforeOverlap,
            sortedPlacement,
            afterOverlap,
        )

    def getIconsInRangeSorted(self, xMin, xMax):
        sortedPlacements = []
        for placement in self.iconPlacements:
            self.checkAndAddToList(sortedPlacements, placement, xMin, xMax)
        return sortedPlacements

    def checkAndAddToList(
        self, sortedPlacements: list, placement: _IconPlacement, xMin, xMax
    ):
        xVal = placement.position.x
        if xVal >= xMin and xVal <= xMax:
            self.addToSortedPlacementList(sortedPlacements, placement)
            return
        xVal += placement.icon.imageWidth
        if xVal >= xMin and xVal <= xMax:
            self.addToSortedPlacementList(sortedPlacements, placement)

    def addToSortedPlacementList(
        self, sortedPlacements: list, placement: _IconPlacement
    ):
        for sPlacement in sortedPlacements:
            if self.isBefore(sPlacement, placement):
                sortedPlacements.insert(sortedPlacements.index(sPlacement), placement)
                return
        sortedPlacements.append(placement)

    def isBefore(self, sortedPlacement: _IconPlacement, placement: _IconPlacement):
        return placement.position.y < sortedPlacement.position.y

    def getIconNames(self):
        names = []
        for placement in self.iconPlacements:
            names.append(placement.icon.fileName)
        return names

    def copy(self):
        return Captcha(self.pImage.copy(), self.fileName)

    def save(self, path: str):
        self.pImage.save(path)


def fromPath(path: str):
    parts = path.split("/")
    fileName = parts[len(parts) - 1]
    return Captcha(PImage.open(path), fileName)
