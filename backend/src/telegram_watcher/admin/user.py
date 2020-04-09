from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import TabularInline
from django.contrib.auth.forms import UserChangeForm

from ..models import User, Subscription


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class SubscriptionInline(TabularInline):
    model = Subscription


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_subscriber')
    list_filter = ('is_superuser', 'is_active', 'groups')

    inlines = [
        SubscriptionInline
    ]

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            fieldsets = (
                (None, {'fields': ('username', 'password', 'timezone', 'is_subscriber', 'stripe_token')}),
                ('Permissions', {'fields': ('is_active', 'is_superuser')}),
                ('Blacklist', {'fields': ('username_blacklist',)}),
                ('Important dates', {'fields': ('last_login', 'date_joined')}),
            )
        else:
            fieldsets = (
                (None, {'fields': ('username', 'password')}),
                ('Blacklist', {'fields': ('username_blacklist',)}),
            )
        return fieldsets

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return False
        elif obj.pk == request.user.pk:
            return True
        else:
            return False