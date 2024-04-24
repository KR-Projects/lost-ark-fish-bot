FILE_NAME = "debug.txt"
DEBUG = True


def debugLine(msg):
    if not DEBUG:
        return
    with open(FILE_NAME, "a") as file:
        file.write(msg + "\n")
        file.flush()
