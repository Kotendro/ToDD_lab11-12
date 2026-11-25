from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import PassLog
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class PassLogListView(BaseModelListView):
    model = PassLog
    fields = "__all__"


class PassLogCreateView(BaseModelCreateView):
    model = PassLog


class PassLogUpdateView(BaseModelUpdateView):
    model = PassLog


class PassLogDeleteView(DeleteView):
    model = PassLog
    success_url = reverse_lazy("main:passlog_list")
    http_method_names = ["post"]
