from django.db import models
from django.utils import timezone


class PostTailorMadeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).order_by(
            '-pub_date'
        )
