from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from django.contrib.admin.actions import delete_selected
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.urls import path
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from .models import (
    User,
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    PredictionAdminForm,
    DataPointAdminForm,
)

# ===========================
# 1. Base Admin Configurations
# ===========================

class PredictorAdminSite(admin.AdminSite):
    """
    Custom admin site for InvestWise Predictor.
    """
    site_header = "InvestWise Predictor Admin"
    site_title = "InvestWise Admin Portal"
    index_title = "Welcome to InvestWise Predictor Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('custom-admin-view/', self.admin_view(self.custom_admin_view), name='custom_admin_view'),
        ]
        return custom_urls + urls

    def custom_admin_view(self, request):
        """
        Custom admin view for additional functionality.
        """
        context = {
            **self.each_context(request),
            'title': 'Custom Admin View',
        }
        return TemplateResponse(request, 'admin/custom_admin_view.html', context)


# Initialize custom admin site
admin_site = PredictorAdminSite(name='investwise_admin')


# ===========================
# 2. ModelAdmin Classes
# ===========================

@admin.register(User, site=admin_site)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the User model.
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions')

    fieldsets = (
        (_('Authentication'), {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Save the user instance and log changes.
        """
        super().save_model(request, obj, form, change)
        if not change:
            logger.info(f"New user created: {obj.username}")


@admin.register(Prediction, site=admin_site)
class PredictionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Prediction model.
    """
    form = PredictionAdminForm
    list_display = ('user', 'sector', 'country', 'predicted_value', 'created_at', 'status')
    list_filter = ('sector', 'country', 'status', 'created_at')
    search_fields = ('user__username', 'sector', 'country')
    ordering = ('-created_at',)
    readonly_fields = ('predicted_value', 'created_at', 'updated_at')

    actions = ['mark_as_completed', 'delete_selected']

    def mark_as_completed(self, request, queryset):
        """
        Custom action to mark selected predictions as completed.
        """
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} predictions marked as completed.")
    mark_as_completed.short_description = "Mark selected predictions as completed"

    def get_queryset(self, request):
        """
        Customize the queryset to include only active predictions.
        """
        queryset = super().get_queryset(request)
        return queryset.filter(Q(status='pending') | Q(status='processing'))

    def has_delete_permission(self, request, obj=None):
        """
        Restrict deletion of predictions with status 'completed'.
        """
        if obj and obj.status == 'completed':
            return False
        return super().has_delete_permission(request, obj)


@admin.register(DataPoint, site=admin_site)
class DataPointAdmin(admin.ModelAdmin):
    """
    Admin configuration for the DataPoint model.
    """
    form = DataPointAdminForm
    list_display = ('indicator', 'value', 'date', 'country', 'source')
    list_filter = ('indicator', 'country', 'date')
    search_fields = ('indicator', 'country', 'source')
    ordering = ('-date',)
    date_hierarchy = 'date'

    def get_form(self, request, obj=None, **kwargs):
        """
        Customize the form to use a date picker widget.
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['date'].widget = AdminDateWidget()
        return form


@admin.register(InvestmentPreference, site=admin_site)
class InvestmentPreferenceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the InvestmentPreference model.
    """
    list_display = ('user', 'preferred_sector', 'preferred_country', 'risk_tolerance')
    list_filter = ('preferred_sector', 'preferred_country', 'risk_tolerance')
    search_fields = ('user__username', 'preferred_sector', 'preferred_country')


@admin.register(RiskProfile, site=admin_site)
class RiskProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the RiskProfile model.
    """
    list_display = ('user', 'profile_type', 'score', 'description')
    list_filter = ('profile_type',)
    search_fields = ('user__username', 'profile_type')


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Notification model.
    """
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)

    def mark_as_read(self, request, queryset):
        """
        Custom action to mark notifications as read.
        """
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

    actions = [mark_as_read]


@admin.register(EconomicIndicator, site=admin_site)
class EconomicIndicatorAdmin(admin.ModelAdmin):
    """
    Admin configuration for the EconomicIndicator model.
    """
    list_display = ('name', 'description', 'unit', 'source')
    search_fields = ('name', 'description', 'source')


@admin.register(SectorPerformance, site=admin_site)
class SectorPerformanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SectorPerformance model.
    """
    list_display = ('sector', 'growth_rate', 'market_size', 'year')
    list_filter = ('sector', 'year')
    search_fields = ('sector',)


# ===========================
# 3. Inline Admin Classes
# ===========================

class DataPointInline(admin.TabularInline):
    """
    Inline admin for DataPoint model.
    """
    model = DataPoint
    extra = 0
    fields = ('indicator', 'value', 'date', 'country', 'source')
    readonly_fields = ('date',)


class PredictionInline(admin.StackedInline):
    """
    Inline admin for Prediction model.
    """
    model = Prediction
    extra = 0
    fields = ('sector', 'country', 'predicted_value', 'status')
    readonly_fields = ('predicted_value',)


# ===========================
# 4. Custom Admin Views
# ===========================

class CustomAdminView(admin.ModelAdmin):
    """
    Custom admin view for advanced functionality.
    """
    change_list_template = 'admin/custom_admin_view.html'

    def changelist_view(self, request, extra_context=None):
        """
        Override the changelist view to include custom data.
        """
        extra_context = extra_context or {}
        extra_context['custom_data'] = {
            'total_users': User.objects.count(),
            'total_predictions': Prediction.objects.count(),
            'recent_notifications': Notification.objects.order_by('-created_at')[:5],
        }
        return super().changelist_view(request, extra_context=extra_context)


# Register the custom admin view
admin_site.register_view('custom-admin-view/', view=CustomAdminView, name='Custom Admin View')


# ===========================
# 5. Utility Functions
# ===========================

def export_as_csv(modeladmin, request, queryset):
    """
    Export selected objects as a CSV file.
    """
    import csv
    from django.http import HttpResponse

    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response
export_as_csv.short_description = "Export selected items as CSV"


# Add the export action to all relevant models
for model_class in [User, Prediction, DataPoint, InvestmentPreference, RiskProfile]:
    admin.site.add_action(export_as_csv)