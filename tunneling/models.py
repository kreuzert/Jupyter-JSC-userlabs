from django.db import models

class Tunnels(models.Model):
    servername = models.TextField(null=False, max_length=300)
    system = models.TextField(null=False, max_length=20)
    node = models.TextField(null=False, max_length=23)
    hostname = models.TextField(null=False, max_length=32)
    port1 = models.IntegerField(null=False)
    port2 = models.IntegerField(null=False)
    date = models.DateTimeField(auto_now=True)
