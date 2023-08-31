from PIL import Image, ImageFont, ImageDraw


def image_set_clock(time):
    time_avatar = 'assets/images/time_avatar.jpg'
    avatar = 'assets/images/avatar.jpg'
    image = Image.open(avatar)
    image.load()
    W, H = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font="assets/fonts/Hacked-KerX.ttf", size=220)
    left, top, right, bottom = font.getbbox(text=time)
    draw.text(((W - right) / 2, (H - bottom) / 2 - 18), time, font=font, fill="#ffffff")
    image.save(time_avatar)
    return time_avatar
