__all__ = [
    "apply_input_rule",
]

from django import forms
from django.core.validators import RegexValidator
from django.db import models


# Явные правила для полей, у которых тип в БД не говорит, что в них можно писать.
# Ключ - model_name, значение - {имя поля: вид ввода}.
MODEL_INPUT_RULES = {
    "client": {
        "last_name": "letters",
        "first_name": "letters",
        "middle_name": "letters",
        "phone_number": "phone",
    },
    "skipass": {
        "card_number": "card",
    },
    "balanceoperation": {
        "amount": "signed_decimal",
    },
}

# Серверная проверка для текстовых видов ввода.
# Числа и даты проверяет сам Django, им валидатор не нужен.
RULE_VALIDATORS = {
    "letters": RegexValidator(
        r"^[A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё\s'-]*$",
        "Допустимы только буквы, пробел, дефис и апостроф.",
    ),
    "phone": RegexValidator(
        r"^\+?[\d\s()-]*\d[\d\s()-]*$",
        "Допустимы только цифры, +, пробел, скобки и дефис.",
    ),
    "card": RegexValidator(
        r"^[A-Za-z0-9-]+$",
        "Допустимы только латинские буквы, цифры и дефис.",
    ),
}

# Виджеты дат и времени: браузер сам не даёт ввести в них буквы.
DATE_WIDGETS = (
    (models.DateTimeField, forms.DateTimeInput, "datetime-local", "%Y-%m-%dT%H:%M"),
    (models.DateField, forms.DateInput, "date", "%Y-%m-%d"),
    (models.TimeField, forms.TimeInput, "time", "%H:%M"),
)


def get_input_rule(model_field):
    """
    Вид ввода для поля модели: явное правило из MODEL_INPUT_RULES,
    иначе - по типу поля. None - ограничений нет (обычный текст).
    """
    model_rules = MODEL_INPUT_RULES.get(model_field.model._meta.model_name, {})
    if model_field.name in model_rules:
        return model_rules[model_field.name]

    if isinstance(model_field, (models.DecimalField, models.FloatField)):
        return "decimal"
    if isinstance(model_field, models.IntegerField):
        return "integer"
    return None


def apply_input_rule(form_field, model_field):
    """
    Настроить поле формы под вид ввода поля модели:
        - даты и время -> нативные инпуты date / datetime-local / time;
        - числа -> текстовый инпут с data-input, лишние символы
          отсекает static/js/input-rules.js (type="number" в Firefox
          пропускает буквы, поэтому он не используется);
        - letters / phone / card -> data-input + серверный валидатор,
          на случай если значение пришло в обход JS.
    """
    if form_field.widget.is_hidden or isinstance(form_field.widget, forms.Select):
        return

    for model_class, widget_class, input_type, input_format in DATE_WIDGETS:
        if isinstance(model_field, model_class):
            form_field.widget = widget_class(
                attrs={**form_field.widget.attrs, "type": input_type},
                format=input_format,
            )
            return

    rule = get_input_rule(model_field)
    if rule is None:
        return

    attrs = {"data-input": rule}
    if rule in ("decimal", "signed_decimal", "integer", "phone"):
        attrs["inputmode"] = "decimal" if "decimal" in rule else "numeric"
    if isinstance(model_field, models.DecimalField):
        attrs["data-max-digits"] = model_field.max_digits
        attrs["data-decimal-places"] = model_field.decimal_places

    old_attrs = {
        key: value
        for key, value in form_field.widget.attrs.items()
        if key not in ("step", "min", "max")
    }
    form_field.widget = forms.TextInput(attrs={**old_attrs, **attrs})

    if rule in RULE_VALIDATORS:
        form_field.validators.append(RULE_VALIDATORS[rule])
