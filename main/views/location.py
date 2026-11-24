from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import Location
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class LocationListView(BaseModelListView):
    model = Location


class LocationCreateView(BaseModelCreateView):
    model = Location


class LocationUpdateView(BaseModelUpdateView):
    model = Location


class LocationDeleteView(DeleteView):
    model = Location
    success_url = reverse_lazy("main:location_list")
    http_method_names = ["post"]
