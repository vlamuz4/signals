import logging
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ProjectGallery
from .validators import strip_exif

logger = logging.getLogger(__name__)


def resize_image(image_field, size: tuple):
    img = Image.open(image_field)
    img = img.convert("RGB")
    img.thumbnail(size)

    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    return ContentFile(buffer.getvalue())


@receiver(pre_save, sender=ProjectGallery)
def clean_exif(sender, instance, **kwargs):
    file = instance.original_image
    cleaned = strip_exif(file)
    instance.original_image.save(
        instance.original_image.name,
        ContentFile(cleaned.read()),
        save=False
    )


@receiver(pre_save, sender=ProjectGallery)
def generate_alt_text(sender, instance, **kwargs):
    if not instance.alt_text:
        instance.alt_text = f"Project {instance.project.name} image"


@receiver(post_save, sender=ProjectGallery)
def process_images(sender, instance, created, **kwargs):
    if not created:
        return

    original = instance.original_image

    thumb = resize_image(original, (150, 150))
    instance.thumbnail.save(f"thumb_{instance.pk}.jpg", thumb, save=False)

    med = resize_image(original, (600, 400))
    instance.medium_image.save(f"medium_{instance.pk}.jpg", med, save=False)

    large = resize_image(original, (1200, 800))
    instance.large_image.save(f"large_{instance.pk}.jpg", large, save=False)

    instance.save()

    logger.info(f"Images generated for project {instance.project.id}")

    send_mail(
        subject="New project image uploaded",
        message=f"A new image was uploaded for project {instance.project.name}.",
        from_email="vlad@example.com",
        recipient_list=[instance.project.owner.email],
        fail_silently=True,
    )
