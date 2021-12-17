from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User as Profile
from django.contrib.auth.models import Group
from .models import User, Client, Contract, Event
from .forms import CustomUserCreation, UserChangeForm


class ContractInline(admin.TabularInline):
    fields = ('status', 'amount', 'payment_due', 'sales_contact', 'id')
    model = Contract
    extra = 0


class EventInline(admin.TabularInline):
    model = Event
    extra = 0


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = CustomUserCreation
    list_display = ('username', 'role', 'is_admin', 'is_staff', 'id')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('client', 'date_created', 'amount', 'status', 'payment_due', 'sales_contact', 'id')
    inlines = [EventInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'mobile', 'role',
                    'company_name', 'date_created', 'sale_contact', 'id')
    inlines = [ContractInline]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'date_updated', 'attendees', 'event_date',
                    'notes', 'client', 'support_contact')
