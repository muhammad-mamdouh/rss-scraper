from django.db import models


class ItemStatus(models.IntegerChoices):
    NEW, READ = range(1, 3)
