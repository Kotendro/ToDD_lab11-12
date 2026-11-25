from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import SalePoint
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class SalePointListView(BaseModelListView):
    model = SalePoint
    fields = "__all__"


class SalePointCreateView(BaseModelCreateView):
    model = SalePoint


class SalePointUpdateView(BaseModelUpdateView):
    model = SalePoint


class SalePointDeleteView(DeleteView):
    model = SalePoint
    success_url = reverse_lazy("main:salepoint_list")
    http_method_names = ["post"]
