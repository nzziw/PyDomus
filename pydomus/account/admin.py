from django.contrib import admin

from .models import Account, TelegramAccount

# Register your models here.
admin.site.register(Account)
admin.site.register(TelegramAccount)
