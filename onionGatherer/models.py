from __future__ import unicode_literals

from django.db import models

class Onions(models.Model):
	url = models.CharField(max_length=20, primary_key=True)
	website = models.CharField(max_length=100)
	lastChecked = models.DateField()

# Create your models here.
