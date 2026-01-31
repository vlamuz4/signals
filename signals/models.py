from django.db import models
from .validators import validate_real_image, validate_min_resolution, validate_exif_safety

class ProjectGallery(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    original_image = models.ImageField(
        upload_to='gallery/original/',
        validators=[validate_real_image, validate_min_resolution, validate_exif_safety]
    )
    thumbnail = models.ImageField(upload_to='gallery/thumbs/', blank=True)
    medium_image = models.ImageField(upload_to='gallery/medium/', blank=True)
    large_image = models.ImageField(upload_to='gallery/large/', blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
