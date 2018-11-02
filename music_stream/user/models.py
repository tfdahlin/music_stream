from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password

# Create your models here.

class User(AbstractUser):
    username = models.TextField(max_length=255, unique=True)
    password = models.TextField(max_length=255)
    name = models.TextField(max_length=255, null=True, blank=True)
    volume = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    can_control = models.BooleanField(default=False)
    

    def check_password(self, raw_password):
        alg, iter, salt, hash = self.password.split('$')
        hashed_pw = make_password(password=raw_password, salt=salt)
        if(hashed_pw == self.password):
            return True
        return False
    
    def __str__(self):
        return self.username
