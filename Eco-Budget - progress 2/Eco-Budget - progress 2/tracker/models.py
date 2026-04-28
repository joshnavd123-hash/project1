from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    sustainability_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.description} - {self.amount}"

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='income')
    amount = models.FloatField()
    source = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.username} - {self.source} - {self.amount}"
