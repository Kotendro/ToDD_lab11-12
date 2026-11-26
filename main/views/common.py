__all__ = [
    "IndexView",
    "BaseModelListView",
    "BaseModelCreateView",
    "BaseModelUpdateView",
    "BaseModelDeleteView",
]

from django.apps import apps
from django.urls import reverse, NoReverseMatch, reverse_lazy
from django.shortcuts import redirect
from django.db.models import ProtectedError, RestrictedError
from django.contrib import messages
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Q


class IndexView(TemplateView):
    """
    Вьюха - страничка с ссылками на все таблицы.
    """

    template_name = "main/common/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups_map = {
            "Сущности": ["client", "skipass"],
            "Операции": ["passlog", "balanceoperation", "drinkpurchase"],
            "Справочники": ["location", "turnstile", "salepoint", "drink"],
        }

        available_models = {}
        for model in apps.get_app_config("main").get_models():
            model_name = model._meta.model_name
            url_name = f"main:{model_name}_list"
            try:
                available_models[model_name] = {
                    "title": model._meta.verbose_name_plural,
                    "url": reverse(url_name),
                }
            except NoReverseMatch:
                continue

        sections = []
        for group_title, model_names in groups_map.items():
            items = [
                available_models[name]
                for name in model_names
                if name in available_models
            ]
            if items:
                sections.append(
                    {
                        "group": group_title,
                        "items": items,
                    }
                )

        context["sections"] = sections
        return context


class BaseModelListView(ListView):
    """
    Вьюха - Общий шаблон для странички list.
    Поддерживает сортировку.
    """

    template_name = "main/common/list.html"
    context_object_name = "rows"
    paginate_by = 25
    fields = None

    def get_fields(self):
        if self.fields == "__all__":
            return [f for f in self.model._meta.fields if not f.primary_key]
        if self.fields is not None:
            return [self.model._meta.get_field(name) for name in self.fields]
        return []

    def get_sortable_fields(self):
        return self.get_fields()

    def apply_sorting(self, queryset):
        """Применить сортировку к queryset."""
        sort_by = self.request.GET.get("sort_by")
        sort_order = self.request.GET.get("sort_order", "asc")

        if sort_by:
            sortable_field_names = [f.name for f in self.get_sortable_fields()]

            if sort_by in sortable_field_names:
                if sort_order == "desc":
                    return queryset.order_by(f"-{sort_by}")
                return queryset.order_by(sort_by)

        return queryset.order_by("-pk")

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.apply_sorting(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        model_name = model._meta.model_name
        fields = self.get_fields()
        sortable_fields = self.get_sortable_fields()

        # Подготовка заголовков с информацией о сортировке
        headers = []
        sort_by = self.request.GET.get("sort_by")
        sort_order = self.request.GET.get("sort_order", "asc")

        for field in fields:
            is_sortable = field in sortable_fields
            header_info = {
                "display_name": field.verbose_name,
                "sortable": is_sortable,
            }

            if is_sortable:
                header_info["field_name"] = field.name
                header_info["is_sorted"] = sort_by == field.name
                header_info["sort_order"] = (
                    sort_order if header_info["is_sorted"] else None
                )

            headers.append(header_info)

        context["headers"] = headers

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model._meta.model_name
        context["cancel_url"] = reverse(f"main:{model_name}_list")
        return context


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


class BaseModelDeleteView(DeleteView):
    """
    Вьюха - Общий шаблон для удаления.
    """

    http_method_names = ["post"]

    def get_success_url(self):
        return reverse(f"main:{self.model._meta.model_name}_list")

    def form_valid(self, form):
        try:
            result = super().form_valid(form)
            return result
        except (ProtectedError, RestrictedError) as e:
            messages.error(
                self.request,
                "Невозможно удалить запись: она используется в других местах. "
                "Пожалуйста, удалите связанные данные или отмените операцию.",
            )
            return redirect(self.get_success_url())
