from django.urls import path
from . import views
from . import models

app_name = "main"


def crud_paths(prefix, model, list_view, create_view, update_view, delete_view):
    name_prefix = model._meta.model_name
    return [
        path(f"{prefix}/", list_view.as_view(), name=f"{name_prefix}_list"),
        path(f"{prefix}/create/", create_view.as_view(), name=f"{name_prefix}_create"),
        path(
            f"{prefix}/<int:pk>/edit/",
            update_view.as_view(),
            name=f"{name_prefix}_edit",
        ),
        path(
            f"{prefix}/<int:pk>/delete/",
            delete_view.as_view(),
            name=f"{name_prefix}_delete",
        ),
    ]


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    *crud_paths(
        "balance",
        models.BalanceOperation,
        views.BalanceOperationListView,
        views.BalanceOperationCreateView,
        views.BalanceOperationUpdateView,
        views.BalanceOperationDeleteView,
    ),
    *crud_paths(
        "clients",
        models.Client,
        views.ClientListView,
        views.ClientCreateView,
        views.ClientUpdateView,
        views.ClientDeleteView,
    ),
    *crud_paths(
        "drinks",
        models.Drink,
        views.DrinkListView,
        views.DrinkCreateView,
        views.DrinkUpdateView,
        views.DrinkDeleteView,
    ),
    *crud_paths(
        "drink-purchases",
        models.DrinkPurchase,
        views.DrinkPurchaseListView,
        views.DrinkPurchaseCreateView,
        views.DrinkPurchaseUpdateView,
        views.DrinkPurchaseDeleteView,
    ),
    *crud_paths(
        "locations",
        models.Location,
        views.LocationListView,
        views.LocationCreateView,
        views.LocationUpdateView,
        views.LocationDeleteView,
    ),
    *crud_paths(
        "pass-logs",
        models.PassLog,
        views.PassLogListView,
        views.PassLogCreateView,
        views.PassLogUpdateView,
        views.PassLogDeleteView,
    ),
    *crud_paths(
        "sale-points",
        models.SalePoint,
        views.SalePointListView,
        views.SalePointCreateView,
        views.SalePointUpdateView,
        views.SalePointDeleteView,
    ),
    *crud_paths(
        "ski-passes",
        models.SkiPass,
        views.SkiPassListView,
        views.SkiPassCreateView,
        views.SkiPassUpdateView,
        views.SkiPassDeleteView,
    ),
    *crud_paths(
        "turnstiles",
        models.Turnstile,
        views.TurnstileListView,
        views.TurnstileCreateView,
        views.TurnstileUpdateView,
        views.TurnstileDeleteView,
    ),
]
