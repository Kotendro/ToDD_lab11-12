from django.urls import reverse_lazy

from main.models import SkiPass
from .common import *


class SkiPassListView(BaseModelListView):
    model = SkiPass
    fields = "__all__"


class SkiPassCreateView(BaseModelCreateView):
    model = SkiPass


class SkiPassUpdateView(BaseModelUpdateView):
    model = SkiPass


class SkiPassDeleteView(BaseModelDeleteView):
    model = SkiPass
