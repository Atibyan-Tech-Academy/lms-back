from django.db.models import Max
from datetime import datetime

def _next_id(prefix, queryset, field):
    year = datetime.now().year
    last_id = queryset.filter(**{f"{field}__startswith": f"{prefix}/{year}/"}).aggregate(
        max_id=Max(field)
    )["max_id"]

    if last_id:
        last_num = int(last_id.split("/")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}/{year}/{new_num:03d}"

def generate_student_id(user_model):
    return _next_id("AOISTU", user_model.objects.all(), "student_id")

def generate_lecturer_id(user_model):
    return _next_id("AOILEC", user_model.objects.all(), "lecturer_id")