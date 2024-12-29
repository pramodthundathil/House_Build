from django.db import models
from django.contrib.auth.models import User

class ProductDetails(models.Model):

    options = (
    ("Bricks", "Bricks"),
    ("Cement", "Cement"),
    ("Sand", "Sand"),
    ("Steel", "Steel"),
    ("Tiles", "Tiles"),
    ("Paint", "Paint"),
    ("Wood", "Wood"),
    ("Glass", "Glass"),
    ("Plumbing", "Plumbing"),
    ("Electrical", "Electrical"),
    ("Roofing", "Roofing"),
    ("Doors", "Doors"),
    ("Windows", "Windows"),
    ("Hardware", "Hardware"),
    ("Insulation", "Insulation"))

    option1 = (
    ("Interior", "Interior"),
    ("Exterior", "Exterior"),
    ("Bathroom", "Bathroom"),
    ("Kitchen", "Kitchen"),
    ("Roofing", "Roofing"),
    ("Flooring", "Flooring"),
    ("Foundation", "Foundation"),
    ("Walls", "Walls"),
    )

    product_name = models.CharField(max_length = 255)
    Product_category = models.CharField(max_length = 255, choices = options)
    Product_subcategory = models.CharField(max_length = 255,choices = option1,null=True)
    product_description = models.CharField(max_length = 255)
    product_price = models.FloatField()
    product_stock = models.IntegerField()
    Product_Image =models.FileField(upload_to="Produc_image",null=True)
    product_availability = models.BooleanField(default = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank  = True)

    def __str__(self):
        return self.product_name
    
class CheckoutAddress(models.Model):
    firstname = models.CharField(max_length = 255)
    lastname  = models.CharField(max_length=255)
    email = models.CharField(max_length = 255)
    mob = models.CharField(max_length = 255)
    address1 = models.CharField(max_length = 255)
    address2 = models.CharField(max_length = 255)
    city = models.CharField(max_length = 255)
    state = models.CharField(max_length = 255)
    pin = models.CharField(max_length = 255)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
     


class CartItems(models.Model):
    product = models.ForeignKey(ProductDetails,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    stock = models.IntegerField()
    price = models.FloatField()
    def __str__(self):
        return str(self.product.product_name)
    
class CheckoutItems(models.Model):
    checkoutaaddress = models.ForeignKey(CheckoutAddress,on_delete = models.SET_NULL,null = True)
    product = models.ForeignKey(ProductDetails,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    stock = models.IntegerField()
    price = models.FloatField()
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255)
    payment_status = models.BooleanField(default=False)
    def __str__(self):
        return self.product


class Review(models.Model):
    product = models.ForeignKey(ProductDetails,on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    review = models.CharField(max_length = 1000)
    name = models.CharField(max_length = 20)
    date = models.DateTimeField(auto_now_add = True,null=True)



# Categorized Services Model
class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Services Model
class Service(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Services_name")
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField( help_text="Duration in minutes", blank=True, null=True)
    image = models.ImageField(upload_to="service_images/", blank=True, null=True)

    def __str__(self):
        return self.name


# Service Booking Model
class ServiceBooking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="bookings")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status_choices = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')
    notes = models.TextField(blank=True, null=True)
    disposal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer.username} - {self.service.name} ({self.appointment_date})"
    




