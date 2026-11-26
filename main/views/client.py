from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import Client
from .common import *


class ClientListView(BaseModelListView):
    model = Client
    fields = "__all__"


class ClientCreateView(BaseModelCreateView):
    model = Client


class ClientUpdateView(BaseModelUpdateView):
    model = Client


class ClientDeleteView(BaseModelDeleteView):
    model = Client
