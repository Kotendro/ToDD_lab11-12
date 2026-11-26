from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from main.models import BalanceOperation
from .common import *


class BalanceOperationListView(BaseModelListView):
    model = BalanceOperation
    fields = "__all__"


class BalanceOperationCreateView(BaseModelCreateView):
    model = BalanceOperation


class BalanceOperationUpdateView(BaseModelUpdateView):
    model = BalanceOperation


class BalanceOperationDeleteView(BaseModelDeleteView):
    model = BalanceOperation
