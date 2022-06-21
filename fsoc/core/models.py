from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)


class friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_friend = models.ForeignKey(User, related_name = 'user_friend', on_delete = models.CASCADE)
    confirmed = models.BooleanField('Confirmed', default=False)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'Friend'
        verbose_name_plural = 'Friends'

