from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    list_filter = ('username', 'email',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
