from django.contrib import admin
from .models import (
    Location, Turnstile, SalePoint, Drink,
    Client, SkiPass, BalanceOperation, PassLog, DrinkPurchase
)

admin.site.register(Location)
admin.site.register(Turnstile)
admin.site.register(SalePoint)
admin.site.register(Drink)
admin.site.register(Client)
admin.site.register(SkiPass)
admin.site.register(BalanceOperation)
admin.site.register(PassLog)
admin.site.register(DrinkPurchase)