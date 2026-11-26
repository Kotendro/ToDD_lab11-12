from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import Drink
from .common import *


class DrinkListView(BaseModelListView):
    model = Drink
    fields = "__all__"


class DrinkCreateView(BaseModelCreateView):
    model = Drink


class DrinkUpdateView(BaseModelUpdateView):
    model = Drink


class DrinkDeleteView(BaseModelDeleteView):
    model = Drink
