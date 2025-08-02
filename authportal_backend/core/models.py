from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Additional fields can be added here if needed
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    memberID = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username

class EBooklet(models.Model):
    name = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='ebooks/')

    def __str__(self):
        return self.name

class UserEBookletSelection(models.Model):
    VIEW_OPTIONS = [
        ('full', 'Full Access'),
        ('preview', 'Preview Only'),
        ('none', 'No Access'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ebooklet = models.ManyToManyField(EBooklet)
    payment_verified = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    view_option = models.CharField(max_length=20, choices=VIEW_OPTIONS, default='none')
    selected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        ebooklet_names = ", ".join([ebooklet.name for ebooklet in self.ebooklet.all()])
        return f"{self.user.username} - {ebooklet_names} - Approved: {self.approved} - View: {self.view_option}"
