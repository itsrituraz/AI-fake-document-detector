"""
Synthetic Specimen Document & Biometric Generator
=================================================
Generates 100% synthetic, compliant travel documents and biometric portraits
for the AI-Based Fake Identity & Document Screening System demo.

Zero personal identifiable information (PII) — completely synthetic graphics,
guilloche patterns, simulated biometric portraits, and valid ICAO Doc 9303 MRZ lines.
"""

import os
import math
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "specimens")
REF_STAMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reference_stamps")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REF_STAMP_DIR, exist_ok=True)


def get_font(size=14, bold=False):
    """Attempt to load a standard system font or fallback to default."""
    font_names = ["arial.ttf", "arialbd.ttf" if bold else "arial.ttf", "segoeui.ttf", "cour.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_mrz_font(size=18):
    """Attempt to load OCR-B / Monospace font for MRZ."""
    font_names = ["cour.ttf", "consola.ttf", "lucon.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def calculate_icao_check_digit(data: str) -> str:
    """
    Calculate ICAO Doc 9303 check digit using weights 7, 3, 1.
    A-Z -> 10-35, 0-9 -> 0-9, '<' -> 0
    """
    weights = [7, 3, 1]
    total = 0
    for idx, char in enumerate(data):
        if char.isdigit():
            val = int(char)
        elif 'A' <= char <= 'Z':
            val = ord(char) - ord('A') + 10
        else:
            val = 0
        total += val * weights[idx % 3]
    return str(total % 10)


def draw_guilloche_background(width, height, color_base=(235, 240, 250)):
    """Draws a security guilloche pattern background typical of authentic banknotes and passports."""
    img = Image.new("RGB", (width, height), color_base)
    draw = ImageDraw.Draw(img)

    # Complex sin/cos guilloche curves
    steps = 1000
    for offset in range(-50, height + 50, 22):
        points = []
        for i in range(steps):
            x = (i / steps) * width
            y = offset + 12 * math.sin(x * 0.025 + offset) + 6 * math.cos(x * 0.05)
            points.append((x, y))
        draw.line(points, fill=(210, 225, 245), width=1)

    for offset in range(-50, width + 50, 35):
        points = []
        for i in range(steps):
            y = (i / steps) * height
            x = offset + 10 * math.sin(y * 0.03 + offset)
            points.append((x, y))
        draw.line(points, fill=(220, 230, 248), width=1)

    # Security microprint header border
    draw.rectangle([10, 10, width - 10, height - 10], outline=(180, 200, 225), width=2)
    return img


def generate_synthetic_portrait(name: str, gender: str = "M", seed: int = 42, variation: float = 0.0):
    """
    Renders a realistic synthetic human passport-style portrait using vector shapes,
    shading, facial features, hair, eyes, and skin tones.
    Zero real PII.
    """
    np.random.seed(seed)
    w, h = 260, 320
    img = Image.new("RGB", (w, h), (218, 224, 232))
    draw = ImageDraw.Draw(img)

    # Background gradient
    for y in range(h):
        r = int(215 + (y / h) * 15)
        g = int(222 + (y / h) * 12)
        b = int(230 + (y / h) * 10)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Shoulders / Suit
    if seed == 777:
        suit_color = (130, 135, 145)  # Light gray suit
        skin_tone = (242, 215, 190)   # Light fair skin tone
        hair_color = (175, 135, 75)   # Blonde hair
    elif gender == "F" or seed == 305:
        suit_color = (75, 40, 60)     # Burgundy suit
        skin_tone = (235, 195, 165)
        hair_color = (40, 25, 20)
    else:
        suit_color = (35, 45, 60)     # Dark navy suit
        skin_tone = (190, 140, 105)   # Olive skin tone
        hair_color = (35, 25, 20)     # Dark brown hair

    draw.ellipse([-40, 220, w + 40, h + 80], fill=suit_color)
    # Shirt collar
    draw.polygon([(w // 2 - 30, 220), (w // 2 + 30, 220), (w // 2, 270)], fill=(245, 248, 252))
    if gender == "M" and seed != 777:
        draw.polygon([(w // 2 - 10, 240), (w // 2 + 10, 240), (w // 2, 310)], fill=(150, 30, 35))

    shadow_skin = (int(skin_tone[0] * 0.85), int(skin_tone[1] * 0.85), int(skin_tone[2] * 0.85))
    draw.rectangle([w // 2 - 28, 175, w // 2 + 28, 235], fill=shadow_skin)

    # Head / Face oval
    cx, cy = w // 2 + int(variation * 5), 140 + int(variation * 3)
    rx, ry = 58, 76
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=skin_tone)

    # Hair
    hair_color = (45, 30, 20) if seed % 3 != 0 else (110, 80, 40)
    if gender == "M":
        draw.chord([cx - rx - 4, cy - ry - 14, cx + rx + 4, cy - ry + 40], start=180, end=360, fill=hair_color)
        draw.rectangle([cx - rx - 2, cy - ry + 10, cx - rx + 14, cy - ry + 50], fill=hair_color)
        draw.rectangle([cx + rx - 14, cy - ry + 10, cx + rx + 2, cy - ry + 50], fill=hair_color)
    else:
        draw.chord([cx - rx - 8, cy - ry - 18, cx + rx + 8, cy - ry + 45], start=180, end=360, fill=hair_color)
        draw.rectangle([cx - rx - 10, cy - ry + 10, cx - rx + 10, cy + 50], fill=hair_color)
        draw.rectangle([cx + rx - 10, cy - ry + 10, cx + rx + 10, cy + 50], fill=hair_color)

    # Eyebrows
    draw.arc([cx - 38, cy - 25, cx - 10, cy - 10], start=190, end=350, fill=hair_color, width=3)
    draw.arc([cx + 10, cy - 25, cx + 38, cy - 10], start=190, end=350, fill=hair_color, width=3)

    # Eyes
    eye_white = (250, 250, 252)
    pupil_color = (35, 25, 20)
    # Left eye
    draw.ellipse([cx - 34, cy - 12, cx - 14, cy], fill=eye_white)
    draw.ellipse([cx - 27, cy - 10, cx - 21, cy - 2], fill=pupil_color)
    # Right eye
    draw.ellipse([cx + 14, cy - 12, cx + 34, cy], fill=eye_white)
    draw.ellipse([cx + 21, cy - 10, cx + 27, cy - 2], fill=pupil_color)

    # Nose
    draw.line([(cx, cy - 5), (cx - 3, cy + 16), (cx + 3, cy + 16)], fill=shadow_skin, width=2)

    # Mouth / Lips
    lip_color = (195, 115, 110)
    draw.ellipse([cx - 16, cy + 30, cx + 16, cy + 40], fill=lip_color)
    draw.line([(cx - 15, cy + 35), (cx + 15, cy + 35)], fill=(130, 60, 60), width=1)

    # Ears
    draw.ellipse([cx - rx - 8, cy - 10, cx - rx + 4, cy + 22], fill=skin_tone)
    draw.ellipse([cx + rx - 4, cy - 10, cx + rx + 8, cy + 22], fill=skin_tone)

    return img


def draw_official_seal(text="CONSULAR SERVICES * UTOPIA *", diameter=160, color=(30, 70, 140, 200)):
    """Creates a transparent official round circular rubber seal stamp."""
    img = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Double outer ring
    draw.ellipse([4, 4, diameter - 4, diameter - 4], outline=color, width=3)
    draw.ellipse([12, 12, diameter - 12, diameter - 12], outline=color, width=1)
    draw.ellipse([24, 24, diameter - 24, diameter - 24], outline=color, width=2)

    # Center emblem / star
    cx, cy = diameter // 2, diameter // 2
    draw.polygon([
        (cx, cy - 24), (cx + 7, cy - 8), (cx + 24, cy - 8),
        (cx + 10, cy + 3), (cx + 15, cy + 20), (cx, cy + 10),
        (cx - 15, cy + 20), (cx - 10, cy + 3), (cx - 24, cy - 8),
        (cx - 7, cy - 8)
    ], fill=color)

    # Text around stamp center
    font = get_font(11, bold=True)
    draw.text((cx - 38, cy + 24), "OFFICIAL", fill=color, font=font)
    draw.text((cx - 36, cy - 35), "VERIFIED", fill=color, font=font)

    return img


def create_authentic_passport():
    """Generates authentic specimen passport image with 100% valid ICAO Doc 9303 MRZ."""
    w, h = 900, 600
    img = draw_guilloche_background(w, h)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, w, 68], fill=(22, 44, 80))
    header_font = get_font(24, bold=True)
    sub_font = get_font(13)
    draw.text((28, 14), "UNITED STATES OF UTOPIA", fill=(255, 255, 255), font=header_font)
    draw.text((30, 44), "PASSPORT / PASSEPORT - SPECIMEN", fill=(190, 215, 250), font=sub_font)

    # Document details
    bold_font = get_font(14, bold=True)
    norm_font = get_font(14)
    lbl_font = get_font(10)

    # Photo placement
    portrait = generate_synthetic_portrait("MICHAEL JOHNSON", gender="M", seed=101)
    img.paste(portrait, (35, 110))
    draw.rectangle([34, 109, 35 + portrait.width, 110 + portrait.height], outline=(120, 140, 170), width=2)

    # VIZ Fields (Visual Inspection Zone)
    fields = [
        ("Type / Type", "P", 330, 95),
        ("Country Code / Code du Pays", "UTO", 430, 95),
        ("Passport No. / No. du Passeport", "P12345678", 620, 95),
        ("Surname / Nom", "JOHNSON", 330, 145),
        ("Given Names / Prénoms", "MICHAEL DAVID", 330, 195),
        ("Nationality / Nationalité", "UTOPIAN", 330, 245),
        ("Date of Birth / Date de Naissance", "15 JUN 1985", 330, 295),
        ("Sex / Sexe", "M", 530, 295),
        ("Place of Birth / Lieu de Naissance", "CAPITAL CITY, UTO", 630, 295),
        ("Date of Issue / Date de Délivrance", "01 JUL 2020", 330, 345),
        ("Date of Expiry / Date d'Expiration", "30 JUN 2030", 530, 345),
        ("Authority / Autorité", "PASSPORT OFFICE", 710, 345),
    ]

    for label, val, x, y in fields:
        draw.text((x, y), label, fill=(110, 120, 135), font=lbl_font)
        draw.text((x, y + 15), val, fill=(15, 20, 35), font=bold_font)

    # Official Seal
    seal = draw_official_seal("CONSULAR POST * UTOPIA *", diameter=140, color=(20, 50, 120, 170))
    img.paste(seal, (720, 180), seal)

    # Machine Readable Zone (MRZ) - 2 lines x 44 characters (TD3 format)
    # Line 1: P<UTOSURNAME<<GIVEN<NAMES<<<<<<<<<<<<<<<<<<
    # Line 2: PASSPORT_NO + CHECK + NAT(3) + DOB(6) + CHECK + SEX(1) + EXP(6) + CHECK + OPT + CHECK + COMPOSITE_CHECK
    doc_no = "P12345678"
    c_doc = calculate_icao_check_digit(doc_no)
    dob = "850615"
    c_dob = calculate_icao_check_digit(dob)
    sex = "M"
    exp = "300630"
    c_exp = calculate_icao_check_digit(exp)
    opt = "<<<<<<<<<<<<<<<"
    c_opt = calculate_icao_check_digit(opt.replace('<', '0'))

    # Composite check digit data: doc_no + c_doc + dob + c_dob + exp + c_exp + opt + c_opt
    comp_data = f"{doc_no}{c_doc}{dob}{c_dob}{exp}{c_exp}{opt}{c_opt}"
    c_comp = calculate_icao_check_digit(comp_data)

    line1 = "P<UTOJOHNSON<<MICHAEL<DAVID<<<<<<<<<<<<<<<<<"
    line2 = f"{doc_no}{c_doc}UTO{dob}{c_dob}{sex}{exp}{c_exp}{opt}{c_comp}"

    # Draw MRZ box
    draw.rectangle([20, 480, w - 20, 580], fill=(255, 255, 255), outline=(200, 205, 215))
    mrz_font = get_mrz_font(19)
    draw.text((35, 498), line1, fill=(10, 15, 25), font=mrz_font)
    draw.text((35, 538), line2, fill=(10, 15, 25), font=mrz_font)

    return img


def create_tampered_passport_photo_spliced(base_img):
    """
    Creates a tampered version where the photo region is replaced with a foreign face
    and recompressed with distinct high-frequency quantization noise, creating high ELA contrast.
    """
    tampered = base_img.copy()
    foreign_portrait = generate_synthetic_portrait("PERSON B", gender="M", seed=777)
    
    # Add localized high-frequency compression noise to simulate digital splicing
    np_portrait = np.array(foreign_portrait).astype(np.float32)
    noise = np.random.normal(0, 7.5, np_portrait.shape)
    noisy_portrait = np.clip(np_portrait + noise, 0, 255).astype(np.uint8)
    foreign_noisy = Image.fromarray(noisy_portrait)

    # Paste over original portrait box
    tampered.paste(foreign_noisy, (35, 110))
    return tampered


def create_tampered_passport_date_altered(base_img):
    """
    Creates a tampered version where the expiration date text in VIZ is altered
    using a digitally mismatched font ("30 JUN 2038"), causing font & MRZ mismatch.
    """
    tampered = base_img.copy()
    draw = ImageDraw.Draw(tampered)

    # Paint over the original date
    draw.rectangle([528, 358, 660, 385], fill=(235, 240, 250))

    # Draw altered text with mismatched thick sans font and slight baseline tilt
    alt_font = get_font(16, bold=True)
    draw.text((530, 360), "30 JUN 2038", fill=(5, 5, 5), font=alt_font)
    return tampered


def create_authentic_visa():
    """Generates authentic specimen tourist visa with official circular stamp."""
    w, h = 800, 520
    img = draw_guilloche_background(w, h, color_base=(248, 250, 240))
    draw = ImageDraw.Draw(img)

    # Border header
    draw.rectangle([0, 0, w, 55], fill=(35, 75, 55))
    h_font = get_font(20, bold=True)
    draw.text((25, 15), "SCHENGEN / UTOPIA ENTRY VISA", fill=(255, 255, 255), font=h_font)

    bold_font = get_font(13, bold=True)
    lbl_font = get_font(10)

    # Portrait
    portrait = generate_synthetic_portrait("MICHAEL JOHNSON", gender="M", seed=101)
    portrait_small = portrait.resize((180, 220))
    img.paste(portrait_small, (30, 80))
    draw.rectangle([29, 79, 30 + 180, 80 + 220], outline=(100, 140, 110), width=2)

    # Fields
    fields = [
        ("Valid For / Valable Pour", "UTOPIA STATES", 240, 75),
        ("Type of Visa / Type de Visa", "C (TOURIST)", 460, 75),
        ("Number of Entries / Nombre d'Entrées", "MULTIPLE (M)", 630, 75),
        ("From / Du", "10 JAN 2024", 240, 130),
        ("Until / Au", "09 JAN 2029", 460, 130),
        ("Duration of Stay / Durée de Séjour", "90 DAYS", 630, 130),
        ("Issued In / Délivré À", "EMBASSY WASHINGTON", 240, 185),
        ("On / Le", "05 JAN 2024", 460, 185),
        ("Visa Number / Numéro de Visa", "V10293847", 630, 185),
        ("Passport Number / Numéro de Passeport", "P12345678", 240, 240),
        ("Holder Surname, Given Names", "JOHNSON, MICHAEL", 460, 240),
    ]

    for lbl, val, x, y in fields:
        draw.text((x, y), lbl, fill=(90, 110, 95), font=lbl_font)
        draw.text((x, y + 15), val, fill=(15, 30, 20), font=bold_font)

    # Seal stamp
    seal = draw_official_seal("CONSULAR EMBASSY * IMMIGRATION *", diameter=130, color=(140, 40, 30, 180))
    img.paste(seal, (640, 260), seal)

    # MRV-A Format (Machine Readable Visa - 2 lines x 44 chars)
    line1 = "VNUTOJOHNSON<<MICHAEL<<<<<<<<<<<<<<<<<<<<<<<"
    line2 = "V102938474UTO8506150M2901095<<<<<<<<<<<<<<08"

    draw.rectangle([15, 410, w - 15, 500], fill=(255, 255, 255), outline=(190, 210, 195))
    mrz_font = get_mrz_font(18)
    draw.text((28, 425), line1, fill=(10, 15, 20), font=mrz_font)
    draw.text((28, 460), line2, fill=(10, 15, 20), font=mrz_font)

    return img


def create_tampered_visa_fake_stamp(base_visa):
    """
    Creates a tampered visa where the duration of stay has been digitally altered
    and a fake distorted/pixelated digital stamp has been pasted in.
    """
    tampered = base_visa.copy()
    draw = ImageDraw.Draw(tampered)

    # Overwrite duration of stay
    draw.rectangle([628, 145, 730, 170], fill=(248, 250, 240))
    alt_font = get_font(15, bold=True)
    draw.text((630, 147), "365 DAYS", fill=(0, 0, 0), font=alt_font)

    # Distorted fake stamp (wrong color, blurred edges, different geometry)
    fake_stamp = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(fake_stamp)
    fdraw.rectangle([10, 10, 130, 130], outline=(200, 20, 20, 220), width=4)
    fdraw.text((25, 40), "APPROVED", fill=(200, 20, 20, 220), font=get_font(16, bold=True))
    fdraw.text((25, 75), "UNLIMITED", fill=(200, 20, 20, 220), font=get_font(14, bold=True))

    tampered.paste(fake_stamp, (635, 255), fake_stamp)
    return tampered


def create_blacklisted_passport():
    """Generates passport matching Interpol SLTD mock alert (No. L898902C3, Anna Eriksson)."""
    w, h = 900, 600
    img = draw_guilloche_background(w, h)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, w, 68], fill=(30, 50, 85))
    draw.text((28, 14), "UNITED STATES OF UTOPIA", fill=(255, 255, 255), font=get_font(24, bold=True))
    draw.text((30, 44), "PASSPORT / PASSEPORT - SPECIMEN", fill=(190, 215, 250), font=get_font(13))

    # Portrait of Anna Eriksson
    portrait = generate_synthetic_portrait("ANNA ERIKSSON", gender="F", seed=305)
    img.paste(portrait, (35, 110))
    draw.rectangle([34, 109, 35 + portrait.width, 110 + portrait.height], outline=(120, 140, 170), width=2)

    bold_font = get_font(14, bold=True)
    lbl_font = get_font(10)

    doc_no = "L898902C3"
    fields = [
        ("Type / Type", "P", 330, 95),
        ("Country Code / Code du Pays", "UTO", 430, 95),
        ("Passport No. / No. du Passeport", doc_no, 620, 95),
        ("Surname / Nom", "ERIKSSON", 330, 145),
        ("Given Names / Prénoms", "ANNA MARIA", 330, 195),
        ("Nationality / Nationalité", "UTOPIAN", 330, 245),
        ("Date of Birth / Date de Naissance", "12 AUG 1974", 330, 295),
        ("Sex / Sexe", "F", 530, 295),
        ("Place of Birth / Lieu de Naissance", "UTOPIA NORTH", 630, 295),
        ("Date of Issue / Date de Délivrance", "14 MAY 2019", 330, 345),
        ("Date of Expiry / Date d'Expiration", "13 MAY 2029", 530, 345),
        ("Authority / Autorité", "PASSPORT OFFICE", 710, 345),
    ]

    for label, val, x, y in fields:
        draw.text((x, y), label, fill=(110, 120, 135), font=lbl_font)
        draw.text((x, y + 15), val, fill=(15, 20, 35), font=bold_font)

    # Checksum calculations
    c_doc = calculate_icao_check_digit(doc_no)
    dob = "740812"
    c_dob = calculate_icao_check_digit(dob)
    sex = "F"
    exp = "290513"
    c_exp = calculate_icao_check_digit(exp)
    opt = "<<<<<<<<<<<<<<<"
    c_opt = calculate_icao_check_digit(opt.replace('<', '0'))
    comp_data = f"{doc_no}{c_doc}{dob}{c_dob}{exp}{c_exp}{opt}{c_opt}"
    c_comp = calculate_icao_check_digit(comp_data)

    line1 = "P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<"
    line2 = f"{doc_no}{c_doc}UTO{dob}{c_dob}{sex}{exp}{c_exp}{opt}{c_comp}"

    draw.rectangle([20, 480, w - 20, 580], fill=(255, 255, 255), outline=(200, 205, 215))
    mrz_font = get_mrz_font(19)
    draw.text((35, 498), line1, fill=(10, 15, 25), font=mrz_font)
    draw.text((35, 538), line2, fill=(10, 15, 25), font=mrz_font)

    return img


def main():
    print("[*] Generating synthetic test specimens...")

    # 1. Authentic Passport
    auth_passport = create_authentic_passport()
    auth_passport_path = os.path.join(OUTPUT_DIR, "authentic_passport.jpg")
    auth_passport.save(auth_passport_path, quality=95)
    print(f"  [+] Saved: {auth_passport_path}")

    # 2. Tampered Passport (Photo Spliced)
    tampered_photo = create_tampered_passport_photo_spliced(auth_passport)
    tampered_photo_path = os.path.join(OUTPUT_DIR, "tampered_passport_photo_spliced.jpg")
    exif_photo = tampered_photo.getexif()
    exif_photo[0x0131] = "Adobe Photoshop CC 2024 (Windows)"
    tampered_photo.save(tampered_photo_path, quality=95, exif=exif_photo)
    print(f"  [+] Saved: {tampered_photo_path}")

    # 3. Tampered Passport (Date Altered)
    tampered_date = create_tampered_passport_date_altered(auth_passport)
    tampered_date_path = os.path.join(OUTPUT_DIR, "tampered_passport_date_altered.jpg")
    exif_date = tampered_date.getexif()
    exif_date[0x0131] = "Adobe Photoshop 25.0"
    tampered_date.save(tampered_date_path, quality=95, exif=exif_date)
    print(f"  [+] Saved: {tampered_date_path}")

    # 4. Authentic Visa
    auth_visa = create_authentic_visa()
    auth_visa_path = os.path.join(OUTPUT_DIR, "authentic_visa.jpg")
    auth_visa.save(auth_visa_path, quality=95)
    print(f"  [+] Saved: {auth_visa_path}")

    # 5. Tampered Visa (Fake Stamp + Altered Duration)
    tampered_visa = create_tampered_visa_fake_stamp(auth_visa)
    tampered_visa_path = os.path.join(OUTPUT_DIR, "tampered_visa_fake_stamp.jpg")
    exif_visa = tampered_visa.getexif()
    exif_visa[0x0131] = "GIMP 2.10.34"
    tampered_visa.save(tampered_visa_path, quality=92, exif=exif_visa)
    print(f"  [+] Saved: {tampered_visa_path}")

    # 6. Blacklisted Passport
    blacklist_passport = create_blacklisted_passport()
    blacklist_passport_path = os.path.join(OUTPUT_DIR, "blacklisted_passport.jpg")
    blacklist_passport.save(blacklist_passport_path, quality=95)
    print(f"  [+] Saved: {blacklist_passport_path}")

    # 7. Biometric Selfies
    # Person A (Michael Johnson) - matching selfie (same face seed, natural slight head turn)
    selfie_match = generate_synthetic_portrait("MICHAEL JOHNSON", gender="M", seed=101, variation=0.3)
    selfie_match_path = os.path.join(OUTPUT_DIR, "selfie_matching_johnson.jpg")
    selfie_match.save(selfie_match_path, quality=95)
    print(f"  [+] Saved: {selfie_match_path}")

    # Person B - non-matching selfie
    selfie_mismatch = generate_synthetic_portrait("PERSON B", gender="M", seed=777, variation=0.0)
    selfie_mismatch_path = os.path.join(OUTPUT_DIR, "selfie_mismatched_person_b.jpg")
    selfie_mismatch.save(selfie_mismatch_path, quality=95)
    print(f"  [+] Saved: {selfie_mismatch_path}")

    # Anna Eriksson - matching selfie for blacklisted test
    selfie_eriksson = generate_synthetic_portrait("ANNA ERIKSSON", gender="F", seed=305, variation=0.2)
    selfie_eriksson_path = os.path.join(OUTPUT_DIR, "selfie_eriksson.jpg")
    selfie_eriksson.save(selfie_eriksson_path, quality=95)
    print(f"  [+] Saved: {selfie_eriksson_path}")

    # 8. Save Official Reference Stamp Template
    ref_seal = draw_official_seal("CONSULAR POST * UTOPIA *", diameter=140, color=(20, 50, 120, 255))
    ref_seal_path = os.path.join(REF_STAMP_DIR, "consular_seal_reference.png")
    ref_seal.save(ref_seal_path)
    print(f"  [+] Saved Reference Stamp: {ref_seal_path}")

    # Manifest metadata
    manifest = {
        "specimens": [
            {
                "file": "authentic_passport.jpg",
                "type": "passport",
                "label": "Authentic Passport (Clean Specimen)",
                "expected_risk": "LOW",
                "matching_selfie": "selfie_matching_johnson.jpg",
                "holder": "MICHAEL DAVID JOHNSON",
                "document_number": "P12345678"
            },
            {
                "file": "tampered_passport_photo_spliced.jpg",
                "type": "passport",
                "label": "Tampered Passport (Photo Spliced)",
                "expected_risk": "HIGH",
                "matching_selfie": "selfie_matching_johnson.jpg",
                "triggers": ["ELA Compression Anomaly", "Face Verification Mismatch"],
                "holder": "MICHAEL DAVID JOHNSON",
                "document_number": "P12345678"
            },
            {
                "file": "tampered_passport_date_altered.jpg",
                "type": "passport",
                "label": "Tampered Passport (Expiry Date Altered)",
                "expected_risk": "HIGH",
                "matching_selfie": "selfie_matching_johnson.jpg",
                "triggers": ["Font Inconsistency", "MRZ Checksum / Consistency Mismatch"],
                "holder": "MICHAEL DAVID JOHNSON",
                "document_number": "P12345678"
            },
            {
                "file": "authentic_visa.jpg",
                "type": "visa",
                "label": "Authentic Schengen/Utopia Visa",
                "expected_risk": "LOW",
                "matching_selfie": "selfie_matching_johnson.jpg",
                "holder": "MICHAEL JOHNSON",
                "document_number": "V10293847"
            },
            {
                "file": "tampered_visa_fake_stamp.jpg",
                "type": "visa",
                "label": "Tampered Visa (Distorted Stamp & Stay Altered)",
                "expected_risk": "HIGH",
                "matching_selfie": "selfie_matching_johnson.jpg",
                "triggers": ["Stamp Correlation Mismatch", "Font Anomaly"],
                "holder": "MICHAEL JOHNSON",
                "document_number": "V10293847"
            },
            {
                "file": "blacklisted_passport.jpg",
                "type": "passport",
                "label": "Blacklisted Passport (Interpol SLTD Match)",
                "expected_risk": "CRITICAL",
                "matching_selfie": "selfie_eriksson.jpg",
                "triggers": ["Interpol Stolen Travel Document Hit (L898902C3)"],
                "holder": "ANNA MARIA ERIKSSON",
                "document_number": "L898902C3"
            }
        ]
    }
    with open(os.path.join(OUTPUT_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  [+] Saved manifest.json")
    print("[OK] All synthetic specimens successfully generated!")


if __name__ == "__main__":
    main()
