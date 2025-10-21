from django.contrib import admin
from .models import Voucher, Transaction


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'current_balance', 'creator', 'created_at']
    list_filter = ['creator', 'created_at']
    search_fields = ['code', 'creator__username']
    readonly_fields = ['code', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['voucher', 'amount', 'transaction_type', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['voucher__code', 'description']
    readonly_fields = ['created_at']
