from PIL import Image

user_sheet = Image.new("RGBA", (130, 1300), None)
all_sheet = Image.new("RGBA", (130, 1300), None)

for i in range(0, 26):
    sprite = Image.open("bar_%05d.png" % i)
    user_sheet.paste(sprite.copy().crop((0, 0, 100, 23)), (0, i * 50))
    all_sheet.paste(sprite.copy().crop((0, 24, 100, 48)), (0, i * 50))

user_sheet.resize((65, 780), Image.ANTIALIAS).save("bright_ldpi.png", optimize=True)
all_sheet.resize((65, 780), Image.ANTIALIAS).save("dark_ldpi.png", optimize=True)

user_sheet.crop((0, 0, 110, 1300)).save("bright_hdpi.png", optimize=True)
all_sheet.crop((0, 0, 110, 1300)).save("dark_hdpi.png", optimize=True)
