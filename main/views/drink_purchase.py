from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import DrinkPurchase
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class DrinkPurchaseListView(BaseModelListView):
    model = DrinkPurchase
    fields = "__all__"


class DrinkPurchaseCreateView(BaseModelCreateView):
    model = DrinkPurchase


class DrinkPurchaseUpdateView(BaseModelUpdateView):
    model = DrinkPurchase


class DrinkPurchaseDeleteView(DeleteView):
    model = DrinkPurchase
    success_url = reverse_lazy("main:drinkpurchase_list")
    http_method_names = ["post"]
