from django.db import models


class Text(models.Model):
    content = models.TextField()
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title