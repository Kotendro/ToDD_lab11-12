from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import Location
from .common import *


class LocationListView(BaseModelListView):
    model = Location
    fields = "__all__"


class LocationCreateView(BaseModelCreateView):
    model = Location


class LocationUpdateView(BaseModelUpdateView):
    model = Location


class LocationDeleteView(BaseModelDeleteView):
    model = Location
