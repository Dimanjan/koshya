"""
Test cases for Voucher System Models
"""
import os
import sys
import django
from decimal import Decimal

# Add the project root to Python path
sys.path.append('/Users/dimanjan/koshya')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voucher_system.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from vouchers.models import Voucher, Transaction


class VoucherModelTest(TestCase):
    """Test cases for Voucher model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass123',
            email='super@example.com'
        )
    
    def test_voucher_creation(self):
        """Test voucher creation with auto-generated code"""
        voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        self.assertIsNotNone(voucher.code)
        self.assertEqual(len(voucher.code), 8)
        self.assertEqual(voucher.current_balance, Decimal('100.00'))
        self.assertEqual(voucher.total_loaded, Decimal('0.00'))
        self.assertFalse(voucher.is_disabled)
        self.assertFalse(voucher.is_sold)
        self.assertEqual(voucher.creator, self.user)
    
    def test_voucher_can_afford(self):
        """Test voucher balance checking"""
        voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        self.assertTrue(voucher.can_afford(Decimal('50.00')))
        self.assertTrue(voucher.can_afford(Decimal('100.00')))
        self.assertFalse(voucher.can_afford(Decimal('150.00')))
    
    def test_voucher_string_representation(self):
        """Test voucher string representation"""
        voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('250.00')
        )
        
        expected = f"Voucher {voucher.code} - Balance: Rs 250.00"
        self.assertEqual(str(voucher), expected)
    
    def test_voucher_soft_disable(self):
        """Test voucher soft disable functionality"""
        voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        # Disable voucher
        voucher.is_disabled = True
        voucher.disabled_at = timezone.now()
        voucher.save()
        
        self.assertTrue(voucher.is_disabled)
        self.assertIsNotNone(voucher.disabled_at)
    
    def test_voucher_mark_sold(self):
        """Test voucher mark as sold functionality"""
        voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        # Mark as sold
        voucher.is_sold = True
        voucher.sold_at = timezone.now()
        voucher.save()
        
        self.assertTrue(voucher.is_sold)
        self.assertIsNotNone(voucher.sold_at)


class TransactionModelTest(TestCase):
    """Test cases for Transaction model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
    
    def test_recharge_transaction(self):
        """Test recharge transaction creation and balance update"""
        initial_balance = self.voucher.current_balance
        initial_total_loaded = self.voucher.total_loaded
        
        transaction = Transaction.objects.create(
            voucher=self.voucher,
            amount=Decimal('50.00'),
            transaction_type='recharge',
            description='Test recharge'
        )
        
        # Refresh voucher from database
        self.voucher.refresh_from_db()
        
        self.assertEqual(self.voucher.current_balance, initial_balance + Decimal('50.00'))
        self.assertEqual(self.voucher.total_loaded, initial_total_loaded + Decimal('50.00'))
        self.assertEqual(transaction.transaction_type, 'recharge')
    
    def test_payment_transaction(self):
        """Test payment transaction creation and balance update"""
        initial_balance = self.voucher.current_balance
        
        transaction = Transaction.objects.create(
            voucher=self.voucher,
            amount=Decimal('30.00'),
            transaction_type='payment',
            description='Test payment'
        )
        
        # Refresh voucher from database
        self.voucher.refresh_from_db()
        
        self.assertEqual(self.voucher.current_balance, initial_balance - Decimal('30.00'))
        self.assertEqual(transaction.transaction_type, 'payment')
    
    def test_transaction_string_representation(self):
        """Test transaction string representation"""
        transaction = Transaction.objects.create(
            voucher=self.voucher,
            amount=Decimal('25.00'),
            transaction_type='recharge',
            description='Test transaction'
        )
        
        expected = f"Recharge of Rs 25.00 for voucher {self.voucher.code}"
        self.assertEqual(str(transaction), expected)


class VoucherQueryTest(TestCase):
    """Test cases for voucher queries and filtering"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        # Create vouchers with different states
        self.active_voucher = Voucher.objects.create(
            creator=self.user1,
            current_balance=Decimal('100.00')
        )
        
        self.disabled_voucher = Voucher.objects.create(
            creator=self.user1,
            current_balance=Decimal('200.00'),
            is_disabled=True,
            disabled_at=timezone.now()
        )
        
        self.sold_voucher = Voucher.objects.create(
            creator=self.user1,
            current_balance=Decimal('300.00'),
            is_sold=True,
            sold_at=timezone.now()
        )
        
        self.other_user_voucher = Voucher.objects.create(
            creator=self.user2,
            current_balance=Decimal('400.00')
        )
    
    def test_active_vouchers_filter(self):
        """Test filtering active vouchers"""
        active_vouchers = Voucher.objects.filter(
            is_disabled=False,
            is_sold=False
        )
        
        self.assertEqual(active_vouchers.count(), 2)  # active_voucher + other_user_voucher
        self.assertIn(self.active_voucher, active_vouchers)
        self.assertIn(self.other_user_voucher, active_vouchers)
        self.assertNotIn(self.disabled_voucher, active_vouchers)
        self.assertNotIn(self.sold_voucher, active_vouchers)
    
    def test_disabled_vouchers_filter(self):
        """Test filtering disabled vouchers"""
        disabled_vouchers = Voucher.objects.filter(is_disabled=True)
        
        self.assertEqual(disabled_vouchers.count(), 1)
        self.assertIn(self.disabled_voucher, disabled_vouchers)
        self.assertNotIn(self.active_voucher, disabled_vouchers)
    
    def test_sold_vouchers_filter(self):
        """Test filtering sold vouchers"""
        sold_vouchers = Voucher.objects.filter(is_sold=True)
        
        self.assertEqual(sold_vouchers.count(), 1)
        self.assertIn(self.sold_voucher, sold_vouchers)
        self.assertNotIn(self.active_voucher, sold_vouchers)
    
    def test_user_specific_vouchers(self):
        """Test filtering vouchers by creator"""
        user1_vouchers = Voucher.objects.filter(creator=self.user1)
        user2_vouchers = Voucher.objects.filter(creator=self.user2)
        
        self.assertEqual(user1_vouchers.count(), 3)
        self.assertEqual(user2_vouchers.count(), 1)
        self.assertIn(self.active_voucher, user1_vouchers)
        self.assertIn(self.other_user_voucher, user2_vouchers)


if __name__ == '__main__':
    import unittest
    unittest.main()
