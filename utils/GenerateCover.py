from PIL import Image, ImageDraw, ImageFont, ImageFilter
import uuid
from utils.Logger import *
from urllib.request import urlopen


KRONA = ImageFont.truetype("etc/KronaOne-Regular.ttf", 48)
KRONA_52 = ImageFont.truetype("etc/KronaOne-Regular.ttf", 52)
ITC_REG = ImageFont.truetype("etc/ITC Avant Garde Gothic LT Book Regular.otf", 48)
KRONA_SMALL = ImageFont.truetype("etc/KronaOne-Regular.ttf", 32)


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight), Image.NEAREST)
    return newImage


async def generate_cover(title, thumbnail, result_file_name):
    temp_file = uuid.uuid4()
    final_img = None
    try:
        logInfo(
            f"Request to generate cover for title : {title} , thumbnail : {thumbnail} , filename : {result_file_name}"
        )
        if len(title) == 0:
            return None
        title = title.strip()
        if len(title) > 25:
            title = title[:22] + str("...")

        downloaded_thumbnail = Image.open(urlopen(thumbnail))

        foreground = Image.open(f"etc/foreground_converted_rgba.png")
        resized_thumbnail = changeImageSize(1280, 720, downloaded_thumbnail)

        background = resized_thumbnail.convert("RGBA")

        Image.alpha_composite(background, foreground).save(
            f"images/{temp_file}.png", optimize=True, quality=20
        )

        img = Image.open(f"images/{temp_file}.png")
        draw = ImageDraw.Draw(img)

        draw.text((10, 580), f"Now Playing", fill="white", font=ITC_REG)

        draw.text((10, 640), f"{title}", fill="white", font=KRONA_52)

        draw.text((985, 20), f"A SkTechHub", fill="white", font=KRONA_SMALL)
        draw.text((1100, 50), f"Product", fill="white", font=KRONA_SMALL)

        img.save(result_file_name, optimize=True, quality=20)
        final_img = result_file_name
    except Exception as ex:
        logException(f"Error while generating cover : {ex}", True)
        final_img = None
    finally:
        return result_file_name if final_img is not None else None


async def generate_blank_cover(result_file_name):
    final_img = None
    try:
        logInfo(f"Request to generate cover for filename : {result_file_name}")
        foreground = Image.open(f"etc/powered_by_sktechhub.png")
        resized_thumbnail = changeImageSize(1280, 720, foreground)
        resized_thumbnail.save(result_file_name, optimize=True, quality=20)
        final_img = result_file_name
    except Exception as ex:
        logException(f"Error while generating cover : {ex}", True)
        final_img = None
    finally:
        return result_file_name if final_img is not None else None
