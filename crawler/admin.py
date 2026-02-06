from django.contrib import admin
from .models import IPO

# Register your models here.
@admin.register(IPO)
class IPOAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'share_type', 'share_group', 'issue_date')
    search_fields = ('company_name', 'share_type')
    list_filter = ('share_type', 'share_group')
