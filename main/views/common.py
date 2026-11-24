from django.apps import apps
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView, ListView, CreateView, UpdateView


class IndexView(TemplateView):
    """
    Вьюха - страничка с ссылками на все таблицы.
    """

    template_name = "main/common/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sections = []

        for model in apps.get_app_config("main").get_models():
            url_name = f"main:{model._meta.model_name}_list"
            try:
                sections.append(
                    {
                        "title": model._meta.verbose_name_plural,
                        "url": reverse(url_name),
                    }
                )
            except NoReverseMatch:
                continue

        context["sections"] = sections
        return context


class BaseModelListView(ListView):
    """
    Вьюха - Общий шаблон для странички list.
    """

    template_name = "main/common/list.html"
    context_object_name = "rows"
    fields = None

    def get_fields(self):
        if self.fields == "__all__":
            return [f for f in self.model._meta.fields if not f.primary_key]
        if self.fields is not None:
            return [self.model._meta.get_field(name) for name in self.fields]
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        model_name = model._meta.model_name
        fields = self.get_fields()

        context["headers"] = [model._meta.verbose_name] + [
            field.verbose_name for field in fields
        ]
        context["title"] = model._meta.verbose_name_plural
        context["create_url"] = reverse(f"main:{model_name}_create")

        rows = []
        for obj in context["object_list"]:
            values = []
            for field in fields:
                display_method = getattr(obj, f"get_{field.name}_display", None)
                val = display_method() if display_method else getattr(obj, field.name)
                values.append("—" if val is None or val == "" else val)

            rows.append(
                {
                    "str_value": str(obj),
                    "values": values,
                    "edit_url": reverse(f"main:{model_name}_edit", args=[obj.pk]),
                    "delete_url": reverse(f"main:{model_name}_delete", args=[obj.pk]),
                }
            )

        context["rows"] = rows
        return context


class BaseFormMixin:
    template_name = "main/common/form.html"
    fields = "__all__"

    def get_success_url(self):
        return reverse(f"main:{self.model._meta.model_name}_list")


class BaseModelCreateView(BaseFormMixin, CreateView):
    """
    Вьюха - Общий шаблон для странички form при создании.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Добавление: {self.model._meta.verbose_name}"
        return context


class BaseModelUpdateView(BaseFormMixin, UpdateView):
    """
    Вьюха - Общий шаблон для странички form при редактировании.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактирование: {self.object}"
        return context
