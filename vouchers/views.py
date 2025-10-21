from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import JsonResponse
from .models import Voucher, Transaction
from .serializers import (
    VoucherSerializer, VoucherCreateSerializer, VoucherRechargeSerializer,
    PaymentSerializer, TransactionSerializer
)
from .permissions import IsAdminOrSuperAdmin


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user account.
    POST /api/register/
    """
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True  # Make all registered users staff
        )
        
        return Response({
            'message': 'User created successfully',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to create user: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """
    Authenticate admin and return token.
    POST /api/get-token/
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user and (user.is_staff or user.is_superuser):
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'is_superuser': user.is_superuser
        })
    else:
        return Response(
            {'error': 'Invalid credentials or insufficient permissions'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class VoucherListCreateView(generics.ListCreateAPIView):
    """
    List all vouchers or create a new voucher.
    GET /api/vouchers/ - List vouchers (admin sees own, superadmin sees all)
    POST /api/vouchers/ - Create new voucher
    """
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VoucherCreateSerializer
        return VoucherSerializer
    
    def get_queryset(self):
        """Return vouchers based on user permissions."""
        if self.request.user.is_superuser:
            # Superadmin sees all non-disabled, non-sold vouchers
            return Voucher.objects.filter(is_disabled=False, is_sold=False)
        else:
            # Admin sees only their own non-disabled, non-sold vouchers
            return Voucher.objects.filter(creator=self.request.user, is_disabled=False, is_sold=False)
    
    def perform_create(self, serializer):
        """Create voucher with authenticated user as creator."""
        serializer.save(creator=self.request.user)


class VoucherDetailView(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a specific voucher.
    GET /api/vouchers/<id>/
    DELETE /api/vouchers/<id>/
    """
    serializer_class = VoucherSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Return vouchers based on user permissions."""
        if self.request.user.is_superuser:
            return Voucher.objects.filter(is_disabled=False)
        else:
            return Voucher.objects.filter(creator=self.request.user, is_disabled=False)
    
    def destroy(self, request, *args, **kwargs):
        """Disable the voucher instead of deleting it."""
        from django.utils import timezone
        instance = self.get_object()
        instance.is_disabled = True
        instance.disabled_at = timezone.now()
        instance.save()
        
        return Response({
            'message': f'Voucher {instance.code} has been disabled successfully',
            'voucher_code': instance.code,
            'disabled_at': instance.disabled_at
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def enable_voucher(request, pk):
    """
    Enable a disabled voucher.
    POST /api/vouchers/<id>/enable/
    """
    try:
        voucher = Voucher.objects.get(pk=pk, is_disabled=True)
        voucher.is_disabled = False
        voucher.disabled_at = None
        voucher.save()
        
        return Response({
            'message': f'Voucher {voucher.code} has been enabled successfully',
            'voucher_code': voucher.code
        }, status=status.HTTP_200_OK)
    except Voucher.DoesNotExist:
        return Response({
            'error': 'Voucher not found or already enabled'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def get_sold_vouchers(request):
    """
    Get sold vouchers for the authenticated user.
    GET /api/vouchers/sold/
    """
    if request.user.is_superuser:
        vouchers = Voucher.objects.filter(is_sold=True)
    else:
        vouchers = Voucher.objects.filter(creator=request.user, is_sold=True)
    
    serializer = VoucherSerializer(vouchers, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def mark_voucher_sold(request, pk):
    """
    Mark a voucher as sold.
    POST /api/vouchers/<id>/mark-sold/
    """
    try:
        voucher = Voucher.objects.get(pk=pk, is_disabled=False, is_sold=False)
        from django.utils import timezone
        voucher.is_sold = True
        voucher.sold_at = timezone.now()
        voucher.save()
        
        return Response({
            'message': f'Voucher {voucher.code} has been marked as sold',
            'voucher_code': voucher.code,
            'sold_at': voucher.sold_at
        }, status=status.HTTP_200_OK)
    except Voucher.DoesNotExist:
        return Response({
            'error': 'Voucher not found, already sold, or disabled'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def get_disabled_vouchers(request):
    """
    Get disabled vouchers for the authenticated user.
    GET /api/vouchers/disabled/
    """
    if request.user.is_superuser:
        vouchers = Voucher.objects.filter(is_disabled=True)
    else:
        vouchers = Voucher.objects.filter(creator=request.user, is_disabled=True)
    
    serializer = VoucherSerializer(vouchers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def get_statistics(request):
    """
    Get voucher statistics including disabled vouchers.
    GET /api/statistics/
    """
    from django.db.models import Sum, Count
    
    # Get all vouchers (including disabled)
    all_vouchers = Voucher.objects.all()
    
    # Get non-disabled vouchers
    active_vouchers = all_vouchers.filter(is_disabled=False)
    
    # Calculate statistics
    total_vouchers = all_vouchers.count()
    active_vouchers_count = active_vouchers.count()
    disabled_vouchers_count = all_vouchers.filter(is_disabled=True).count()
    sold_vouchers_count = all_vouchers.filter(is_sold=True).count()
    
    # Calculate total balance from active vouchers only
    total_balance = active_vouchers.aggregate(
        total=Sum('current_balance')
    )['total'] or 0
    
    return Response({
        'total_vouchers': total_vouchers,
        'active_vouchers': active_vouchers_count,
        'disabled_vouchers': disabled_vouchers_count,
        'sold_vouchers': sold_vouchers_count,
        'total_balance': float(total_balance)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrSuperAdmin])
def recharge_voucher(request, code):
    """
    Recharge a voucher with 100, 200, or 500.
    POST /api/vouchers/<code>/recharge/
    """
    try:
        voucher = Voucher.objects.get(code=code)
    except Voucher.DoesNotExist:
        return Response(
            {'error': 'Voucher not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if user has permission to recharge this voucher
    if not request.user.is_superuser and voucher.creator != request.user:
        return Response(
            {'error': 'You can only recharge your own vouchers'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = VoucherRechargeSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        
        # Create recharge transaction
        transaction = Transaction.objects.create(
            voucher=voucher,
            amount=amount,
            transaction_type='recharge',
            description=f'Recharge of Rs {amount}'
        )
        
        return Response({
            'message': f'Voucher {code} recharged with Rs {amount}',
            'new_balance': voucher.current_balance,
            'transaction': TransactionSerializer(transaction).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def make_payment(request):
    """
    Public endpoint to make payment using voucher.
    POST /api/pay/
    """
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        voucher = serializer.context['voucher']
        amount = serializer.validated_data['amount']
        
        # Create payment transaction
        transaction = Transaction.objects.create(
            voucher=voucher,
            amount=amount,
            transaction_type='payment',
            description=f'Payment of Rs {amount}'
        )
        
        return Response({
            'message': f'Payment of Rs {amount} successful',
            'voucher_code': voucher.code,
            'remaining_balance': voucher.current_balance,
            'transaction_id': transaction.id
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_voucher_balance(request, code):
    """
    Public endpoint to check voucher balance.
    GET /api/vouchers/<code>/balance/
    """
    try:
        voucher = Voucher.objects.get(code=code)
        
        # Check if voucher is disabled or sold
        if voucher.is_disabled:
            return Response({
                'voucher_code': voucher.code,
                'balance': float(voucher.current_balance),
                'status': 'disabled',
                'message': 'Voucher is disabled'
            }, status=status.HTTP_200_OK)
        
        if voucher.is_sold:
            return Response({
                'voucher_code': voucher.code,
                'balance': float(voucher.current_balance),
                'status': 'sold',
                'message': 'Voucher has been sold'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'voucher_code': voucher.code,
            'balance': float(voucher.current_balance),
            'status': 'active',
            'message': 'Voucher is active and ready for use'
        }, status=status.HTTP_200_OK)
        
    except Voucher.DoesNotExist:
        return Response({
            'error': 'Voucher not found',
            'voucher_code': code
        }, status=status.HTTP_404_NOT_FOUND)


# Frontend Views
def dashboard_view(request):
    """Main dashboard view"""
    return render(request, 'vouchers/dashboard.html')


def payment_view(request):
    """Public payment page"""
    return render(request, 'vouchers/payment.html')


def index_view(request):
    """Home page"""
    return render(request, 'vouchers/index.html')
