from django.db import models

# Create your models here.
class Stock(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class StockData(models.Model):
    company_code = models.CharField(max_length=50)
    date = models.DateField()
    last_transaction_price = models.FloatField(null=True, blank=True)
    max_price = models.FloatField(null=True, blank=True)
    min_price = models.FloatField(null=True, blank=True)
    average_price = models.FloatField(null=True, blank=True)
    trading_volume_best = models.FloatField(null=True, blank=True)
    total_trading_volume = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.company_code} - {self.date}"
