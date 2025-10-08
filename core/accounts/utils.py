from django.db.models import Max
from datetime import datetime


def _next_id(prefix, queryset, field):
    """
    Generates the next unique ID for a given model and field.
    Format: PREFIX/YYYY/NNN
    Example: AOISTU/2025/001
    """
    year = datetime.now().year
    prefix_with_year = f"{prefix}/{year}/"

    # Get the last ID that starts with the prefix and year
    last_id = queryset.filter(**{f"{field}__startswith": prefix_with_year}).aggregate(
        max_id=Max(field)
    )["max_id"]

    if last_id:
        try:
            last_num = int(last_id.split("/")[-1])
        except (ValueError, IndexError):
            last_num = 0
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}/{year}/{new_num:03d}"


def generate_student_id(model_class):
    """Generates a unique student ID."""
    return _next_id("AOISTU", model_class.objects.all(), "student_id")


def generate_lecturer_id(model_class):
    """Generates a unique lecturer ID."""
    return _next_id("AOILEC", model_class.objects.all(), "lecturer_id")
