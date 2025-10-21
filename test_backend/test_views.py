"""
Test cases for Voucher System API Views
"""
import os
import sys
import django
import json
from decimal import Decimal

# Add the project root to Python path
sys.path.append('/Users/dimanjan/koshya')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voucher_system.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from vouchers.models import Voucher, Transaction


class VoucherAPITest(APITestCase):
    """Test cases for Voucher API endpoints"""
    
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
        
        # Create tokens for authentication
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
        
        # Create test vouchers
        self.voucher1 = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00'),
            total_loaded=Decimal('100.00')
        )
        
        self.voucher2 = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('200.00'),
            total_loaded=Decimal('200.00'),
            is_disabled=True
        )
        
        self.voucher3 = Voucher.objects.create(
            creator=self.superuser,
            current_balance=Decimal('300.00'),
            total_loaded=Decimal('300.00'),
            is_sold=True
        )
    
    def test_get_token_authentication(self):
        """Test token authentication endpoint"""
        url = reverse('get-token')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_get_token_invalid_credentials(self):
        """Test token authentication with invalid credentials"""
        url = reverse('get-token')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_voucher_list_authenticated(self):
        """Test voucher list endpoint with authentication"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-list-create')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only active vouchers
    
    def test_voucher_list_unauthenticated(self):
        """Test voucher list endpoint without authentication"""
        url = reverse('voucher-list-create')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_voucher_creation(self):
        """Test voucher creation endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-list-create')
        data = {'initial_value': 150.00}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if voucher was created
        voucher = Voucher.objects.get(code=response.data['code'])
        self.assertEqual(voucher.creator, self.user)
        self.assertEqual(voucher.current_balance, Decimal('150.00'))
        self.assertEqual(voucher.total_loaded, Decimal('150.00'))
    
    def test_voucher_detail(self):
        """Test voucher detail endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-detail', kwargs={'pk': self.voucher1.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], self.voucher1.code)
    
    def test_voucher_disable(self):
        """Test voucher disable endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-detail', kwargs={'pk': self.voucher1.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if voucher was disabled
        self.voucher1.refresh_from_db()
        self.assertTrue(self.voucher1.is_disabled)
        self.assertIsNotNone(self.voucher1.disabled_at)
    
    def test_disabled_vouchers_endpoint(self):
        """Test disabled vouchers endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('disabled-vouchers')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], self.voucher2.code)
    
    def test_sold_vouchers_endpoint(self):
        """Test sold vouchers endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.superuser_token.key}')
        url = reverse('sold-vouchers')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['code'], self.voucher3.code)
    
    def test_mark_voucher_sold(self):
        """Test mark voucher as sold endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('mark-voucher-sold', kwargs={'pk': self.voucher1.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if voucher was marked as sold
        self.voucher1.refresh_from_db()
        self.assertTrue(self.voucher1.is_sold)
        self.assertIsNotNone(self.voucher1.sold_at)
    
    def test_enable_voucher(self):
        """Test enable voucher endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('enable-voucher', kwargs={'pk': self.voucher2.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if voucher was enabled
        self.voucher2.refresh_from_db()
        self.assertFalse(self.voucher2.is_disabled)
        self.assertIsNone(self.voucher2.disabled_at)
    
    def test_statistics_endpoint(self):
        """Test statistics endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('statistics')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check statistics data
        self.assertIn('total_vouchers', response.data)
        self.assertIn('active_vouchers', response.data)
        self.assertIn('disabled_vouchers', response.data)
        self.assertIn('sold_vouchers', response.data)
        self.assertIn('total_balance', response.data)
    
    def test_recharge_voucher(self):
        """Test voucher recharge endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-recharge', kwargs={'code': self.voucher1.code})
        data = {'amount': 100}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if voucher was recharged
        self.voucher1.refresh_from_db()
        self.assertEqual(self.voucher1.current_balance, Decimal('200.00'))
        self.assertEqual(self.voucher1.total_loaded, Decimal('200.00'))
    
    def test_recharge_invalid_amount(self):
        """Test voucher recharge with invalid amount"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-recharge', kwargs={'code': self.voucher1.code})
        data = {'amount': 50}  # Invalid amount (not 100, 200, or 500)
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_recharge_nonexistent_voucher(self):
        """Test recharge with nonexistent voucher code"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-recharge', kwargs={'code': 'INVALID'})
        data = {'amount': 100}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaymentAPITest(APITestCase):
    """Test cases for Payment API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00'),
            total_loaded=Decimal('100.00')
        )
        
        self.disabled_voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('50.00'),
            is_disabled=True
        )
    
    def test_make_payment_success(self):
        """Test successful payment"""
        url = reverse('make-payment')
        data = {
            'voucher_code': self.voucher.code,
            'amount': 25.00
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if voucher balance was updated
        self.voucher.refresh_from_db()
        self.assertEqual(self.voucher.current_balance, Decimal('75.00'))
    
    def test_make_payment_insufficient_balance(self):
        """Test payment with insufficient balance"""
        url = reverse('make-payment')
        data = {
            'voucher_code': self.voucher.code,
            'amount': 150.00  # More than available balance
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_make_payment_invalid_voucher(self):
        """Test payment with invalid voucher code"""
        url = reverse('make-payment')
        data = {
            'voucher_code': 'INVALID',
            'amount': 25.00
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_make_payment_disabled_voucher(self):
        """Test payment with disabled voucher"""
        url = reverse('make-payment')
        data = {
            'voucher_code': self.disabled_voucher.code,
            'amount': 25.00
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PermissionsTest(APITestCase):
    """Test cases for API permissions"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='adminpass123',
            is_staff=True
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            password='superpass123'
        )
        
        # Create tokens
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin)
        self.superuser_token = Token.objects.create(user=self.superuser)
    
    def test_user_can_only_see_own_vouchers(self):
        """Test that users can only see their own vouchers"""
        # Create vouchers for different users
        user_voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        admin_voucher = Voucher.objects.create(
            creator=self.admin,
            current_balance=Decimal('200.00')
        )
        
        # Test user can only see their own vouchers
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        url = reverse('voucher-list-create')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['code'], user_voucher.code)
    
    def test_superuser_can_see_all_vouchers(self):
        """Test that superuser can see all vouchers"""
        # Create vouchers for different users
        user_voucher = Voucher.objects.create(
            creator=self.user,
            current_balance=Decimal('100.00')
        )
        
        admin_voucher = Voucher.objects.create(
            creator=self.admin,
            current_balance=Decimal('200.00')
        )
        
        # Test superuser can see all vouchers
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.superuser_token.key}')
        url = reverse('voucher-list-create')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


if __name__ == '__main__':
    import unittest
    unittest.main()
