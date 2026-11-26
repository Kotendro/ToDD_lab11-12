from django.urls import reverse_lazy

from main.models import PassLog
from .common import *


class PassLogListView(BaseModelListView):
    model = PassLog
    fields = "__all__"


class PassLogCreateView(BaseModelCreateView):
    model = PassLog


class PassLogUpdateView(BaseModelUpdateView):
    model = PassLog


class PassLogDeleteView(BaseModelDeleteView):
    model = PassLog
