from django.db import models
from django.conf import settings


class Master(models.Model):
    name = models.CharField(max_length=255)
    expirience_years = models.IntegerField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name


class Style(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title
    

class Sketch(models.Model):
    title = models.CharField(max_length=255)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    style = models.ForeignKey(Style, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    

class Client(models.Model):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=16)

    def __str__(self):
        return self.name


class Session(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    master = models.ForeignKey(Master, on_delete=models.CASCADE)
    sketch = models.ForeignKey(Sketch, on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20)

    def __str__(self):
        sketch_title = self.sketch.title if self.sketch else "Эскиз не выбран"
        return f"Сеанс для {self.client.name} ({sketch_title})"
