from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import BalanceOperation
from .common import BaseModelListView, BaseModelCreateView, BaseModelUpdateView


class BalanceOperationListView(BaseModelListView):
    model = BalanceOperation
    fields = "__all__"


class BalanceOperationCreateView(BaseModelCreateView):
    model = BalanceOperation


class BalanceOperationUpdateView(BaseModelUpdateView):
    model = BalanceOperation


class BalanceOperationDeleteView(DeleteView):
    model = BalanceOperation
    success_url = reverse_lazy("main:balanceoperation_list")
    http_method_names = ["post"]
