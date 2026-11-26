__all__ = [
    "ModelFilterForm",
]

from django import forms
from django.db import models


class ModelFilterForm(forms.Form):
    """
    Динамическая форма фильтрации по полям модели.

    Имя каждого поля формы совпадает с ORM-лукапом, поэтому
    cleaned_data можно сразу передать в queryset.filter(**...).

    Как фильтруется каждый тип поля модели:
        - choices        -> select, точное совпадение;
        - ForeignKey     -> select связных объектов, точное совпадение;
        - BooleanField   -> select Да/Нет;
        - числа и время  -> диапазон "от" / "до" (__gte / __lte);
        - DateTimeField  -> диапазон дат (__date__gte / __date__lte);
        - остальное      -> текст, вхождение без учёта регистра (__icontains).

    Для шаблона собирается self.groups: список
    {"label": подпись поля модели, "fields": [BoundField, ...]}.
    """

    def __init__(self, *args, model_fields, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = []

        for model_field in model_fields:
            names = self.add_filter_fields(model_field)
            self.groups.append(
                {
                    "label": model_field.verbose_name,
                    "fields": [self[name] for name in names],
                }
            )

    def add_filter_fields(self, model_field):
        """
        Добавить в форму поля фильтрации для одного поля модели.
        Возвращает список имён добавленных полей формы.
        """
        name = model_field.name
        label = model_field.verbose_name

        if model_field.choices:
            self.fields[name] = forms.ChoiceField(
                label=label,
                required=False,
                choices=[("", "Все"), *model_field.choices],
            )
            return [name]

        if isinstance(model_field, models.ForeignKey):
            self.fields[name] = forms.ModelChoiceField(
                label=label,
                required=False,
                queryset=model_field.related_model.objects.all(),
                empty_label="Все",
            )
            return [name]

        if isinstance(model_field, models.BooleanField):
            self.fields[name] = forms.NullBooleanField(
                label=label,
                required=False,
                widget=forms.Select(
                    choices=[("", "Все"), ("true", "Да"), ("false", "Нет")]
                ),
            )
            return [name]

        if isinstance(model_field, models.DateTimeField):
            return self.add_range_fields(
                f"{name}__date",
                label,
                forms.DateField,
                forms.DateInput,
                {"type": "date"},
            )

        if isinstance(model_field, models.DateField):
            return self.add_range_fields(
                name,
                label,
                forms.DateField,
                forms.DateInput,
                {"type": "date"},
            )

        if isinstance(model_field, models.TimeField):
            return self.add_range_fields(
                name,
                label,
                forms.TimeField,
                forms.TimeInput,
                {"type": "time"},
            )

        if isinstance(model_field, models.DecimalField):
            return self.add_range_fields(
                name,
                label,
                forms.DecimalField,
                forms.NumberInput,
                {"step": "any"},
            )

        if isinstance(model_field, models.FloatField):
            return self.add_range_fields(
                name,
                label,
                forms.FloatField,
                forms.NumberInput,
                {"step": "any"},
            )

        if isinstance(model_field, models.IntegerField):
            return self.add_range_fields(
                name,
                label,
                forms.IntegerField,
                forms.NumberInput,
                {},
            )

        lookup = f"{name}__icontains"
        self.fields[lookup] = forms.CharField(label=label, required=False)
        return [lookup]

    def add_range_fields(self, lookup, label, field_class, widget_class, attrs):
        """Добавить пару полей "от" / "до" для лукапа."""
        names = []
        for suffix, placeholder in (("gte", "от"), ("lte", "до")):
            name = f"{lookup}__{suffix}"
            self.fields[name] = field_class(
                label=f"{label} {placeholder}",
                required=False,
                widget=widget_class(attrs={**attrs, "placeholder": placeholder}),
            )
            names.append(name)
        return names

    def get_filters(self):
        """
        Словарь для queryset.filter(**...).
        Берутся только заполненные и прошедшие валидацию поля,
        поэтому кривое значение в одном фильтре не ломает остальные.
        """
        if not self.is_bound:
            return {}

        self.is_valid()
        return {
            name: value
            for name, value in self.cleaned_data.items()
            if value is not None and value != ""
        }

    @property
    def is_active(self):
        """Применён ли хотя бы один фильтр."""
        return bool(self.get_filters())
