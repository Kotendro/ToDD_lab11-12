__all__ = [
    "IndexView",
    "BaseModelListView",
    "BaseModelCreateView",
    "BaseModelUpdateView",
    "BaseModelDeleteView",
]

from urllib.parse import urlencode

from django.apps import apps
from django.urls import reverse, NoReverseMatch, reverse_lazy
from django.shortcuts import redirect
from django.db import models
from django.db.models import ProtectedError, RestrictedError
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Q

from main.filters import ModelFilterForm


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


class ReturnUrlMixin:
    """
    Миксин - адрес возврата на list после операции.
    Адрес берётся из параметра next (GET или POST), чтобы пользователь
    вернулся на ту же страницу со всеми query (page, сортировка, фильтры).
    """

    return_url_param = "next"

    def get_list_url(self):
        return reverse(f"main:{self.model._meta.model_name}_list")

    def get_return_url(self):
        """
        Адрес из next, если он безопасный (только наш хост),
        иначе - list модели без query.
        """
        url = self.request.POST.get(self.return_url_param) or self.request.GET.get(
            self.return_url_param
        )
        is_safe = url and url_has_allowed_host_and_scheme(
            url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        )
        return url if is_safe else self.get_list_url()


class BaseModelListView(ListView):
    """
    Вьюха - Общий шаблон для странички list.
    Поддерживает сортировку, фильтрацию, пагинацию
    и кнопку "создать на основании".
    """

    template_name = "main/common/list.html"
    context_object_name = "rows"
    paginate_by = 25
    fields = None
    return_url_param = ReturnUrlMixin.return_url_param

    def get_fields(self):
        if self.fields == "__all__":
            return [f for f in self.model._meta.fields if not f.primary_key]
        if self.fields is not None:
            return [self.model._meta.get_field(name) for name in self.fields]
        return []

    def get_sortable_fields(self):
        return self.get_fields()

    def get_filterable_fields(self):
        return self.get_fields()

    def get_filter_form(self):
        """Форма фильтров по текущим GET-параметрам (создаётся один раз)."""
        if not hasattr(self, "_filter_form"):
            self._filter_form = ModelFilterForm(
                self.request.GET,
                model_fields=self.get_filterable_fields(),
            )
        return self._filter_form

    def apply_filters(self, queryset):
        """Применить фильтры к queryset."""
        return queryset.filter(**self.get_filter_form().get_filters())

    def apply_sorting(self, queryset):
        """Применить сортировку к queryset."""
        sort_by = self.request.GET.get("sort_by")
        sort_order = self.request.GET.get("sort_order", "asc")

        if sort_by:
            sortable_field_names = [f.name for f in self.get_sortable_fields()]

            if sort_by in sortable_field_names:
                if sort_order == "desc":
                    return queryset.order_by(f"-{sort_by}", "-pk")
                return queryset.order_by(sort_by, "-pk")

        return queryset.order_by("-pk")

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.apply_filters(queryset)
        return self.apply_sorting(queryset)

    def get_valid_page_url(self):
        """
        Если page из query больше не существует (например, удалили
        последний объект на последней странице или сузили фильтр),
        вернуть адрес ближайшей валидной страницы с теми же query.
        Если page валидна - вернуть None.
        """
        page = self.request.GET.get(self.page_kwarg)
        if page is None:
            return None

        queryset = self.get_queryset()
        paginator = self.get_paginator(
            queryset,
            self.get_paginate_by(queryset),
            orphans=self.get_paginate_orphans(),
            allow_empty_first_page=self.get_allow_empty(),
        )

        try:
            number = int(page)
        except ValueError:
            number = paginator.num_pages if page == "last" else 1

        valid_number = min(max(number, 1), paginator.num_pages)
        if str(valid_number) == page:
            return None

        query = self.request.GET.copy()
        if valid_number == 1:
            query.pop(self.page_kwarg)
        else:
            query[self.page_kwarg] = str(valid_number)

        return f"{self.request.path}?{query.urlencode()}"

    def get(self, request, *args, **kwargs):
        valid_page_url = self.get_valid_page_url()
        if valid_page_url:
            return redirect(valid_page_url)
        return super().get(request, *args, **kwargs)

    def with_return_url(self, url, **params):
        """Добавить к url параметр next с текущим адресом list и доп. параметры."""
        params[self.return_url_param] = self.request.get_full_path()
        return f"{url}?{urlencode(params)}"

    def get_based_on_options(self):
        """
        Варианты для кнопки "создать на основании": все модели,
        у которых есть ForeignKey на текущую модель и есть страничка создания.
        Например, для Клиента - Ски-пасс (поле client).
        """
        options = []
        for relation in self.model._meta.related_objects:
            if not isinstance(relation.field, models.ForeignKey):
                continue

            related_model = relation.related_model
            try:
                create_url = reverse(f"main:{related_model._meta.model_name}_create")
            except NoReverseMatch:
                continue

            options.append(
                {
                    "title": related_model._meta.verbose_name,
                    "create_url": create_url,
                    "field_name": relation.field.name,
                }
            )
        return options

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
                header_info["next_sort_order"] = (
                    "desc" if header_info["sort_order"] == "asc" else "asc"
                )

            headers.append(header_info)

        context["headers"] = headers

        context["title"] = model._meta.verbose_name_plural
        context["create_url"] = self.with_return_url(
            reverse(f"main:{model_name}_create")
        )
        context["filter_form"] = self.get_filter_form()
        context["based_on_options"] = self.get_based_on_options()
        context["return_url"] = self.request.get_full_path()
        context["return_url_param"] = self.return_url_param

        rows = []
        for obj in context["object_list"]:
            values = []
            for field in fields:
                display_method = getattr(obj, f"get_{field.name}_display", None)
                val = display_method() if display_method else getattr(obj, field.name)
                values.append("—" if val is None or val == "" else val)

            rows.append(
                {
                    "pk": obj.pk,
                    "values": values,
                    "edit_url": self.with_return_url(
                        reverse(f"main:{model_name}_edit", args=[obj.pk])
                    ),
                    "delete_url": self.with_return_url(
                        reverse(f"main:{model_name}_delete", args=[obj.pk])
                    ),
                }
            )

        context["rows"] = rows
        return context


class BaseFormMixin(ReturnUrlMixin):
    template_name = "main/common/form.html"
    fields = "__all__"

    def get_success_url(self):
        return self.get_return_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.get_return_url()
        return context


class BaseModelCreateView(BaseFormMixin, CreateView):
    """
    Вьюха - Общий шаблон для странички form при создании.
    Связные объекты (ForeignKey) можно подставить через query,
    например ?client=5 - так работает "создать на основании".
    """

    def get_initial(self):
        initial = super().get_initial()
        for field in self.model._meta.fields:
            if isinstance(field, models.ForeignKey) and field.name in self.request.GET:
                initial[field.name] = self.request.GET[field.name]
        return initial

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


class BaseModelDeleteView(ReturnUrlMixin, DeleteView):
    """
    Вьюха - Общий шаблон для удаления.
    """

    http_method_names = ["post"]

    def get_success_url(self):
        return self.get_return_url()

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
