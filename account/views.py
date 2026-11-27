from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView


@method_decorator(login_not_required, name="dispatch")
class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "account/register.html"
    success_url = reverse_lazy("account:login")