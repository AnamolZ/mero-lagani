from django.db import models

# Create your models here.
class IPO(models.Model):
    company_name = models.CharField(max_length=255)
    share_type = models.CharField(max_length=255)
    share_group = models.CharField(max_length=255)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.company_name} ({self.share_type}, {self.share_group})"