from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

# =========================
# SCALE / CONSTANTS
# =========================
SCALE = 3

W_BASE = 500
W = W_BASE * SCALE

PAD = 20 * SCALE
HEADER_GAP = 35 * SCALE
ROW_H = 26 * SCALE
NOTE_LINE_H = 16 * SCALE
NOTE_PAD = 16 * SCALE

# =========================
# STYLE SYSTEM
# =========================
THEMES = {
    "energy": ("#e8f1ff", "#3b82f6"),
    "fat": ("#fff4db", "#f59e0b"),
    "carbs": ("#ffe7d6", "#f97316"),
    "protein": ("#e8f7ee", "#22c55e"),
    "other": ("#f1f5f9", "#94a3b8"),

    "fatvit": ("white", "#7c3aed"),
    "bvit": ("white", "#0ea5e9"),
    "vitc": ("white", "#e11d48"),

    "mineral-electrolyte": ("white", "#14b8a6"),
    "mineral-structural": ("white", "#64748b"),
    "mineral-trace": ("white", "#d4a017"),

    "phyto": ("#f8fafc", "#16a34a"),
    "organic-acid": ("#f8fafc", "#6366f1"),
    "macronutrient": ("#fff4db", "#f59e0b"),
}

NOTE_STYLE = {
    "bg": "#fafafa",
    "border": "#999",
    "text": "#333"
}

# =========================
# FONT CACHE (GLOBAL)
# =========================
def load_fonts():
    try:
        return {
            "normal": ImageFont.truetype("arial.ttf", 14 * SCALE),
            "bold": ImageFont.truetype("arialbd.ttf", 14 * SCALE),
            "header": ImageFont.truetype("arialbd.ttf", 18 * SCALE),
        }
    except:
        f = ImageFont.load_default()
        return {"normal": f, "bold": f, "header": f}

FONTS = load_fonts()

# =========================
# HEIGHT CALC (FAST)
# =========================
def calculate_label_height(label):
    h = (20 + 40 + 10) * SCALE

    for row in label["rows"]:
        if row["type"] == "note":
            lines = row["text"].count("\n") + 1
            h += lines * NOTE_LINE_H + NOTE_PAD
        else:
            h += ROW_H

    return h + 30 * SCALE

# =========================
# TEXT WIDTH (FASTER)
# =========================
def text_width(draw, text, font):
    # fastest available path in PIL 9+
    try:
        return font.getlength(text)
    except:
        return draw.textlength(text, font=font)

# =========================
# RENDER LABEL (IN MEMORY)
# =========================
def render_label(label, H):
    img = Image.new("RGB", (W, H), "#f2f2f2")
    draw = ImageDraw.Draw(img)

    x = PAD
    y = PAD

    # CARD
    draw.rounded_rectangle(
        (10 * SCALE, 10 * SCALE, W - 10 * SCALE, H - 10 * SCALE),
        radius=12 * SCALE,
        fill="white",
        outline="#e5e7eb",
        width=2 * SCALE
    )

    # HEADER
    draw.text((x, y), label["title"], fill="black", font=FONTS["header"])
    y += HEADER_GAP

    draw.line((x, y, W - x, y), fill="black", width=2 * SCALE)
    y += 10 * SCALE

    # ROWS
    for row in label["rows"]:
        rtype = row.get("type", "other")

        if rtype == "note":
            lines = row["text"].split("\n")
            box_h = len(lines) * NOTE_LINE_H + NOTE_PAD

            draw.rectangle(
                (x, y, W - x, y + box_h),
                fill=NOTE_STYLE["bg"],
                outline=NOTE_STYLE["border"],
                width=1 * SCALE
            )

            ty = y + 6 * SCALE
            for line in lines:
                draw.text((x + 8 * SCALE, ty),
                          line,
                          fill=NOTE_STYLE["text"],
                          font=FONTS["normal"])
                ty += NOTE_LINE_H

            y += box_h + 10 * SCALE
            continue

        left = row.get("left", "")
        right = row.get("right", "")
        indent = row.get("indent", 0) * 18 * SCALE

        bg, accent = THEMES[rtype]

        font = FONTS["bold"] if row.get("bold", False) or rtype == "macronutrient" else FONTS["normal"]

        # row background
        draw.rectangle((x, y - 2 * SCALE, W - x, y + 24 * SCALE), fill=bg)
        draw.rectangle((x, y - 2 * SCALE, x + 5 * SCALE, y + 24 * SCALE), fill=accent)

        # text
        draw.text((x + 10 * SCALE + indent, y), left, fill="black", font=font)

        rw = text_width(draw, right, font)
        draw.text((W - x - rw, y), right, fill="black", font=font)

        draw.line((x, y + 22 * SCALE, W - x, y + 22 * SCALE),
                  fill=(220, 220, 220),
                  width=1 * SCALE)

        y += ROW_H

    return img

# =========================
# SHARPEN (IN MEMORY)
# =========================
def make_crisp(img):
    return img.filter(ImageFilter.UnsharpMask(
        radius=0.7,
        percent=70,
        threshold= 2 
    ))

# =========================
# COMBINE IMAGES
# =========================
def combine(images, out_path):
    width = images[0].width
    height = sum(img.height for img in images)

    combined = Image.new("RGB", (width, height))

    y = 0
    for img in images:
        combined.paste(img, (0, y))
        y += img.height

    combined.save(out_path, optimize=True)

# =========================
# MAIN PIPELINE
# =========================
def render_all(data, out_dir="temp"):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    heights = [calculate_label_height(l) for l in data["labels"]]
    outputs = []

    for i, label in enumerate(data["labels"]):
        img = render_label(label, heights[i])
        img = make_crisp(img)

        out_path = out_dir / f"label_{i+1}.png"
        img.save(out_path, "PNG", dpi=(300, 300), optimize=False)

        outputs.append(out_path)

    return outputs

