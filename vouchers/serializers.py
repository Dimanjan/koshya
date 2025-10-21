from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Voucher, Transaction


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_staff', 'is_superuser']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model."""
    
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class VoucherSerializer(serializers.ModelSerializer):
    """Serializer for Voucher model."""
    creator = UserSerializer(read_only=True)
    transactions = TransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Voucher
        fields = ['id', 'code', 'current_balance', 'total_loaded', 'creator', 'created_at', 'updated_at', 'transactions']
        read_only_fields = ['id', 'code', 'creator', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Create a new voucher with the authenticated user as creator."""
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class VoucherCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating vouchers with initial value."""
    initial_value = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    
    class Meta:
        model = Voucher
        fields = ['initial_value']
    
    def create(self, validated_data):
        """Create voucher with initial balance."""
        initial_value = validated_data.pop('initial_value')
        voucher = Voucher.objects.create(
            creator=self.context['request'].user,
            current_balance=0,  # Start with 0 balance
            total_loaded=0  # Start with 0 total loaded
        )
        
        # Create initial recharge transaction
        Transaction.objects.create(
            voucher=voucher,
            amount=initial_value,
            transaction_type='recharge',
            description=f'Initial voucher creation with Rs {initial_value}'
        )
        
        return voucher
    
    def to_representation(self, instance):
        """Return voucher details after creation."""
        return VoucherSerializer(instance).data


class VoucherRechargeSerializer(serializers.Serializer):
    """Serializer for voucher recharge."""
    amount = serializers.ChoiceField(choices=[100, 200, 500])
    
    def validate_amount(self, value):
        """Validate recharge amount."""
        if value not in [100, 200, 500]:
            raise serializers.ValidationError("Amount must be 100, 200, or 500")
        return value


class PaymentSerializer(serializers.Serializer):
    """Serializer for public payment endpoint."""
    voucher_code = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    
    def validate_voucher_code(self, value):
        """Validate that voucher exists and is active."""
        try:
            voucher = Voucher.objects.get(code=value)
            self.context['voucher'] = voucher
        except Voucher.DoesNotExist:
            raise serializers.ValidationError("Invalid voucher code")
        return value
    
    def validate(self, data):
        """Validate payment amount against voucher balance and status."""
        voucher = self.context.get('voucher')
        amount = data['amount']
        
        # Check if voucher is disabled or sold
        if voucher.is_disabled or voucher.is_sold:
            raise serializers.ValidationError(
                "Voucher is disabled or sold and cannot be used for payments."
            )
        
        if not voucher.can_afford(amount):
            raise serializers.ValidationError(
                f"Insufficient balance. Available: Rs {voucher.current_balance}, Required: Rs {amount}"
            )
        
        return data
