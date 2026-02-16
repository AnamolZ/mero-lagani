from django.db import models

class IPO(models.Model):
    """
    Model representing an Initial Public Offering (IPO) entry.

    Attributes:
        company_name (str): Name of the company issuing the IPO.
        share_type (str): Type of shares being offered.
        share_group (str): Classification/group of the shares.
        issue_date (date): Date the IPO record was created (auto-set on creation).
    """

    company_name = models.CharField(max_length=255)  # Name of the issuing company
    share_type = models.CharField(max_length=255)    # Type of shares offered
    share_group = models.CharField(max_length=255)   # Share classification/group
    issue_date = models.DateField(auto_now_add=True) # Record creation date

    def __str__(self):
        """Return a human-readable representation of the IPO instance."""
        return f"{self.company_name} ({self.share_type}, {self.share_group})"