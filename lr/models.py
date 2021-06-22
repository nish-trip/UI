from django.db import models
    
class Receipt(models.Model):

    lr_number = models.CharField(max_length = 254)
    customer_name = models.CharField(max_length = 254)
    origin = models.CharField(max_length = 254)
    destination = models.CharField(max_length = 254)
    booking_date = models.CharField(max_length = 254)
    number_of_boxes = models.IntegerField()

    def __str__(self):
        return customer_name
    