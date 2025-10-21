from django.db import models
from django.contrib.auth.models import User
import uuid


class Voucher(models.Model):
    """Model representing a voucher with unique code and balance."""
    code = models.CharField(max_length=20, unique=True)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_loaded = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_vouchers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_disabled = models.BooleanField(default=False)
    disabled_at = models.DateTimeField(null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        """Override save to generate unique code if not provided."""
        if not self.code:
            self.code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Voucher {self.code} - Balance: Rs {self.current_balance}"

    def can_afford(self, amount):
        """Check if voucher has sufficient balance for a transaction."""
        return self.current_balance >= amount


class Transaction(models.Model):
    """Model representing a transaction (payment or recharge) for a voucher."""
    TRANSACTION_TYPES = [
        ('recharge', 'Recharge'),
        ('payment', 'Payment'),
    ]

    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type.title()} of Rs {self.amount} for voucher {self.voucher.code}"

    def save(self, *args, **kwargs):
        """Override save to update voucher balance."""
        super().save(*args, **kwargs)
        
        # Update voucher balance based on transaction type
        if self.transaction_type == 'recharge':
            self.voucher.current_balance += self.amount
            self.voucher.total_loaded += self.amount
        elif self.transaction_type == 'payment':
            self.voucher.current_balance -= self.amount
        
        self.voucher.save()
