"""成果物3の「引き継ぎフォルダ」のうち、番号で変わらない材料を folder/ に作る（1回だけ実行）。
申込の3ファイルは番号で変わるので make.py が作る。
写真には架空の撮影場所（GPS）を入れてある。人物は線画で、実在の人ではない。
"""
import os
from PIL import Image, ImageDraw, ImageFont

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "folder")
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
os.makedirs(D, exist_ok=True)


def font(n):
    return ImageFont.truetype(FONT, n)


def gps_save(img, path):
    exif = img.getexif()
    gps = exif.get_ifd(0x8825)
    gps.update({1: "N", 2: (35.0, 36.0, 12.0), 3: "E", 4: (139.0, 36.0, 34.0)})
    exif[0x8825] = gps
    exif[0x9003] = "2026:11:12 15:40:00"  # DateTimeOriginal
    img.save(path, "JPEG", exif=exif, quality=85)


def photo(name, title, draw_fn):
    img = Image.new("RGB", (1200, 900), (236, 232, 222))
    d = ImageDraw.Draw(img)
    draw_fn(d)
    d.rectangle([0, 820, 1200, 900], fill=(40, 40, 40))
    d.text((24, 838), f"下見 11/12 撮影　{title}", font=font(36), fill="white")
    gps_save(img, os.path.join(D, name))


def entrance(d):
    d.rectangle([420, 180, 780, 780], outline=(80, 60, 40), width=10, fill=(190, 160, 120))
    d.rectangle([380, 90, 820, 160], fill=(30, 70, 140))
    d.text((440, 100), "C棟 入口", font=font(48), fill="white")


def room(d):
    for x in range(3):
        for y in range(3):
            d.rectangle([150 + x * 330, 250 + y * 170, 400 + x * 330, 330 + y * 170], fill=(150, 110, 70))
    d.rectangle([200, 60, 1000, 200], fill=(30, 80, 50))
    d.text((230, 100), "C棟1階105教室", font=font(56), fill="white")


def power(d):
    d.rectangle([450, 250, 750, 600], fill="white", outline="gray", width=6)
    for y in (330, 470):
        d.rectangle([540, y, 560, y + 60], fill="black")
        d.rectangle([640, y, 660, y + 60], fill="black")
    d.text((420, 640), "壁のコンセント（2口）", font=font(40), fill="black")
    # 右下に名札が写り込んでいる（架空の名前）
    d.rectangle([900, 560, 1180, 800], fill="white", outline=(200, 0, 0), width=8)
    d.text((930, 590), "名札", font=font(40), fill=(200, 0, 0))
    d.text((930, 660), "ヤマダ", font=font(56), fill="black")
    d.text((930, 730), "施設課", font=font(36), fill="black")


def board(d):
    d.rectangle([200, 120, 1000, 740], fill=(180, 140, 90), outline=(90, 60, 30), width=12)
    for i, (x, y) in enumerate([(260, 180), (620, 180), (260, 460), (620, 460)]):
        d.rectangle([x, y, x + 300, y + 230], fill="white")
    d.text((640, 220), "掲示場所", font=font(44), fill="black")


def room_face(d):
    room(d)
    d.ellipse([520, 300, 720, 500], fill=(250, 220, 190), outline="black", width=5)
    d.ellipse([570, 370, 590, 390], fill="black")
    d.ellipse([650, 370, 670, 390], fill="black")
    d.arc([580, 410, 660, 460], 0, 180, fill="black", width=5)
    d.rectangle([540, 500, 700, 780], fill=(60, 90, 160))


def hallway(d):
    d.polygon([(0, 0), (500, 350), (500, 550), (0, 820)], fill=(200, 200, 200))
    d.polygon([(1200, 0), (700, 350), (700, 550), (1200, 820)], fill=(200, 200, 200))
    d.rectangle([500, 350, 700, 550], fill=(120, 120, 120))


photo("IMG_3101.jpg", "入口", entrance)
photo("IMG_3102.jpg", "教室", room)
photo("IMG_3103.jpg", "電源", power)
photo("IMG_3104.jpg", "掲示板", board)
photo("IMG_3105.jpg", "教室（人が写っている）", room_face)
photo("IMG_3106.jpg", "廊下", hallway)


def flyer(name, date, body):
    img = Image.new("RGB", (1080, 1350), (255, 248, 230))
    d = ImageDraw.Draw(img)
    d.text((80, 100), "スマホ動画ミニ講座", font=font(84), fill=(180, 60, 20))
    y = 320
    for line in body:
        d.text((80, y), line, font=font(52), fill="black")
        y += 90
    d.text((80, 1240), f"作成 {date}", font=font(36), fill="gray")
    img.save(os.path.join(D, name))


flyer("チラシ.png", "11/01", ["11月27日（金）16:20〜17:30", "A棟2階201教室", "定員なし・参加無料"])
flyer("チラシ_修正.png", "11/08", ["11月27日（金）16:20〜17:30", "C棟1階105教室", "定員なし・参加無料"])

img = Image.new("RGB", (1200, 900), "white")
d = ImageDraw.Draw(img)
d.rectangle([100, 100, 500, 400], outline="black", width=6)
d.text((180, 220), "A棟", font=font(60), fill="black")
d.rectangle([650, 400, 1100, 800], outline="black", width=6, fill=(220, 240, 255))
d.text((720, 560), "C棟 105教室", font=font(56), fill="black")
d.line([500, 300, 650, 550], fill="red", width=8)
d.text((60, 820), "会場の地図　更新 10/30", font=font(40), fill="black")
img.save(os.path.join(D, "会場の地図.png"))

GUIDE = """件名：スマホ動画ミニ講座のご案内
参加者のみなさま
スマホ動画ミニ講座は、11月27日（金）16:20〜17:30に開きます。
会場は{room}です。
スマホを充電してお越しください。
"""
for fn, upd, room in (("案内文_最終.txt", "11/05", "A棟2階201教室"),
                      ("案内文_下書き.txt", "11/09", "C棟1階105教室"),
                      ("案内文_下書き_修正版.txt", "11/13", "C棟1階105教室（C棟の正面入口からお入りください）")):
    with open(os.path.join(D, fn), "w", encoding="utf-8") as f:
        f.write(f"更新: {upd}\n" + GUIDE.format(room=room))
print("ok")
