from django.urls import reverse_lazy

from main.models import Turnstile
from .common import *


class TurnstileListView(BaseModelListView):
    model = Turnstile
    fields = "__all__"


class TurnstileCreateView(BaseModelCreateView):
    model = Turnstile


class TurnstileUpdateView(BaseModelUpdateView):
    model = Turnstile


class TurnstileDeleteView(BaseModelDeleteView):
    model = Turnstile
