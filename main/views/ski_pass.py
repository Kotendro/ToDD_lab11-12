from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import SkiPass
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class SkiPassListView(BaseModelListView):
    model = SkiPass
    fields = ["client", "balance", "status"]
    paginate_by = 25


class SkiPassCreateView(BaseModelCreateView):
    model = SkiPass


class SkiPassUpdateView(BaseModelUpdateView):
    model = SkiPass


class SkiPassDeleteView(DeleteView):
    model = SkiPass
    success_url = reverse_lazy("main:skipass_list")
    http_method_names = ["post"]
