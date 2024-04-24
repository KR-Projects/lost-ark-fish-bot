from imageArchive import ImageArchive
import icon
import debug
import os
import random
import imageCutter
import datetime
import random
import string
import datetime


TEST_SET_BASEDIR = "./test_set"
TRAIN_SET_BASEDIR = "./training_set"
EXCLAMATION_MARK_MIN_VISIBILITY = 0.75
TRAIN_RATE = 0.7
TRUE_IMGS_SUBDIR_NAME = "true"
FALSE_IMGS_SUBDIR_NAME = "false"
EXCLAMATION_MARKS_SUBDIR_NAME = "exclamation_mark_ingame"
CAPTCHA_IMG_WIDTH = 100
CAPTCHA_IMG_HEIGHT = 200


bgArchive = ImageArchive("wallpaper.zip")

debug.DEBUG = False


salt = 64356
random.seed(hash(datetime.datetime.now().timestamp() + salt))


def random_name(length: int) -> str:
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    all = lower + upper + num
    random_name = random.choices(all, k=length)
    return "".join(random_name)


def generate():
    numOfCaptcha = 0
    prevProgress = 0
    curImage = 0
    totalImages = bgArchive.getImageAmount()
    while True:
        nextBg = bgArchive.nextImage()
        if not nextBg:
            break
        for captcha in imageCutter.cutIntoCaptchas(
            nextBg, CAPTCHA_IMG_WIDTH, CAPTCHA_IMG_HEIGHT
        ):
            dirRandom = random.choice(range(100))
            baseDir = TEST_SET_BASEDIR
            if dirRandom < 70:
                baseDir = TRAIN_SET_BASEDIR
            captcha.save(f"{baseDir}/{FALSE_IMGS_SUBDIR_NAME}/{random_name(20)}.bmp")
            iicon = getRandomIcon()
            captcha.addIconsRandom([iicon], EXCLAMATION_MARK_MIN_VISIBILITY)
            captcha.save(f"{baseDir}/{TRUE_IMGS_SUBDIR_NAME}/{random_name(20)}.bmp")
            numOfCaptcha += 1
        curImage += 1
        progress = int(curImage / totalImages * 100)
        if progress > prevProgress:
            print(f"{progress}%")
            prevProgress = progress
    print("done")


def getRandomIcon():
    fileName = random.choice(os.listdir(EXCLAMATION_MARKS_SUBDIR_NAME))
    return icon.fromPath(f"{EXCLAMATION_MARKS_SUBDIR_NAME}/{fileName}")


def create_all_dirs():
    os.makedirs(f"{TEST_SET_BASEDIR}/{TRUE_IMGS_SUBDIR_NAME}", exist_ok=True)
    os.makedirs(f"{TEST_SET_BASEDIR}/{FALSE_IMGS_SUBDIR_NAME}", exist_ok=True)
    os.makedirs(f"{TRAIN_SET_BASEDIR}/{TRUE_IMGS_SUBDIR_NAME}", exist_ok=True)
    os.makedirs(f"{TRAIN_SET_BASEDIR}/{FALSE_IMGS_SUBDIR_NAME}", exist_ok=True)


create_all_dirs()
generate()
