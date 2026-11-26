from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import DrinkPurchase
from .common import *


class DrinkPurchaseListView(BaseModelListView):
    model = DrinkPurchase
    fields = "__all__"


class DrinkPurchaseCreateView(BaseModelCreateView):
    model = DrinkPurchase


class DrinkPurchaseUpdateView(BaseModelUpdateView):
    model = DrinkPurchase


class DrinkPurchaseDeleteView(BaseModelDeleteView):
    model = DrinkPurchase
