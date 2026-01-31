from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO

def validate_real_image(file):
    try:
        img = Image.open(file)
        img.verify()
    except Exception:
        raise ValidationError("Файл не є справжнім зображенням.")

def validate_min_resolution(file):
    img = Image.open(file)
    w, h = img.size
    if w < 300 or h < 200:
        raise ValidationError("Зображення має бути мінімум 300x200.")

def validate_exif_safety(file):
    try:
        img = Image.open(file)
        exif = img.getexif()
        for tag_id, value in exif.items():
            if isinstance(value, bytes) and len(value) > 5000:
                raise ValidationError("EXIF містить підозрілий контент.")
    except Exception:
        pass

def strip_exif(file):
    img = Image.open(file)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)

    buffer = BytesIO()
    clean.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer

