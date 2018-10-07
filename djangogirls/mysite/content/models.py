from django.db import models

# Create your models here.

class ovs1(models.Model):
    name = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class ovs2(models.Model):
    name = models.CharField(max_length=100)
    port = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class ns1(models.Model):
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

class ns2(models.Model):
    name = models.CharField(max_length=100)
    address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

class command(models.Model):
    address = models.GenericIPAddressField()
    user = models.CharField(max_length=100)
    passwd = models.CharField(max_length=100)
    bridge = models.CharField(max_length=100)
    interface = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


