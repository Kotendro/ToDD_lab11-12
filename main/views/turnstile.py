from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import Turnstile
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class TurnstileListView(BaseModelListView):
    model = Turnstile
    fields = ["pass_price"]


class TurnstileCreateView(BaseModelCreateView):
    model = Turnstile


class TurnstileUpdateView(BaseModelUpdateView):
    model = Turnstile


class TurnstileDeleteView(DeleteView):
    model = Turnstile
    success_url = reverse_lazy("main:turnstile_list")
    http_method_names = ["post"]
