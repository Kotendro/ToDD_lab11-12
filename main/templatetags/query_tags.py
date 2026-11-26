from django import template
from django.utils.html import format_html_join

register = template.Library()


def _split_keys(keys):
    """Строка вида "sort_by sort_order" -> множество ключей."""
    return set(keys.split()) if keys else set()


def _filter_query(query, only=None, exclude=None):
    """
    Копия QueryDict, в которой оставлены только ключи из only
    и/или убраны ключи из exclude.
    """
    query = query.copy()
    only_keys = _split_keys(only)
    exclude_keys = _split_keys(exclude)

    for key in list(query.keys()):
        if (only_keys and key not in only_keys) or key in exclude_keys:
            query.pop(key)

    return query


@register.simple_tag(takes_context=True)
def query_replace(context, **kwargs):
    """
    Текущий query string с заменёнными параметрами.
    Параметр со значением None или "" удаляется.

    Пример: {% query_replace page=2 %} -> "?sort_by=price&page=2"
    """
    query = context["request"].GET.copy()

    for key, value in kwargs.items():
        if value is None or value == "":
            query.pop(key, None)
        else:
            query[key] = str(value)

    return f"?{query.urlencode()}"


@register.simple_tag(takes_context=True)
def query_only(context, keys):
    """
    Текущий query string, в котором оставлены только указанные ключи.

    Пример: {% query_only "sort_by sort_order" %}
    """
    query = _filter_query(context["request"].GET, only=keys)
    return f"?{query.urlencode()}"


@register.simple_tag(takes_context=True)
def query_hidden_inputs(context, only=None, exclude=None):
    """
    Hidden-инпуты для текущих GET-параметров.
    Нужны GET-формам, чтобы при отправке не терять остальные query.

    Пример: {% query_hidden_inputs exclude="page" %}
    """
    query = _filter_query(context["request"].GET, only=only, exclude=exclude)
    return format_html_join(
        "",
        '<input type="hidden" name="{}" value="{}">',
        ((key, value) for key, values in query.lists() for value in values),
    )
