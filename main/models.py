from django.db import models

class Carrier(models.Model):
    name = models.CharField(max_length=100)
    states = models.CharField(max_length=255)

    def __str__(self):
        return self.name
