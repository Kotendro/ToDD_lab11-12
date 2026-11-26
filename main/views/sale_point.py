from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import SalePoint
from .common import *


class SalePointListView(BaseModelListView):
    model = SalePoint
    fields = "__all__"


class SalePointCreateView(BaseModelCreateView):
    model = SalePoint


class SalePointUpdateView(BaseModelUpdateView):
    model = SalePoint


class SalePointDeleteView(BaseModelDeleteView):
    model = SalePoint
