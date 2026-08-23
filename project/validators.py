from django.core.exceptions import ValidationError


def validate_image_size(image):
    max_size_mb = 10
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"حجم الصورة أكبر من {max_size_mb} ميجابايت.")