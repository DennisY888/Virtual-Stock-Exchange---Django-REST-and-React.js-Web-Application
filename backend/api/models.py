from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

# Signal to create or save the Profile whenever a User is created or saved
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.db.models import CheckConstraint, Q


# Profile model to extend the built-in User model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cash = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00, validators=[MinValueValidator(Decimal('0.00'))])

    def __str__(self):
        return self.user.username



# Signal to create the Profile whenever a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)



# Portfolio model to track each user's stock holdings
class Portfolio(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='portfolios')
    symbol = models.CharField(max_length=10)
    shares = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.user.username} - {self.symbol} ({self.shares} shares)"

    class Meta:
        unique_together = ('user', 'symbol')



# History model to record each transaction (buy/sell)
class History(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='transactions')
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    shares = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    method = models.CharField(max_length=4)  # e.g., 'buy' or 'sell'
    price = models.DecimalField(max_digits=15, decimal_places=2)
    transacted = models.DateTimeField(auto_now_add=True)
    new_cash = models.DecimalField(max_digits=15, decimal_places=2) # new remaining cash after this transaction
    total_value = models.DecimalField(max_digits=15, decimal_places=2) # price * shares

    def __str__(self):
        return f"{self.user.user.username} - {self.method} {self.shares} shares of {self.symbol} at {self.price}"

    class Meta:
        ordering = ['-transacted']
        constraints = [
            CheckConstraint(check=Q(shares__gte=1), name='shares_positive')
        ]



# Watchlist model to track stocks that a user is watching
class Watchlist(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='watchlist')
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.user.username} - Watching {self.symbol}"
    
    class Meta:
        unique_together = ('user', 'symbol')