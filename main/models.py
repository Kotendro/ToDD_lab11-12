__all__ = [
    "BalanceOperation",
    "Client",
    "Drink",
    "DrinkPurchase",
    "Location",
    "PassLog",
    "SalePoint",
    "SkiPass",
    "Turnstile",
]


from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField("Название локации", max_length=100, unique=True)

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

    def __str__(self):
        return self.location_name


class Turnstile(models.Model):
    turnstile_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="turnstiles",
        verbose_name="Локация",
    )
    turnstile_name = models.CharField("Название турникета", max_length=50)
    pass_price = models.DecimalField(
        "Стоимость прохода",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Турникет"
        verbose_name_plural = "Турникеты"
        constraints = [
            models.CheckConstraint(
                condition=Q(pass_price__gte=Decimal("0.00")),
                name="turnstile_pass_price_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.turnstile_name} ({self.location.location_name})"


class SalePoint(models.Model):
    sale_point_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="sale_points",
        verbose_name="Локация",
    )
    cafe_name = models.CharField("Название кафе", max_length=100)
    open_time = models.TimeField("Время открытия", null=True, blank=True)
    close_time = models.TimeField("Время закрытия", null=True, blank=True)

    class Meta:
        verbose_name = "Точка продажи"
        verbose_name_plural = "Точки продажи"

    def __str__(self):
        return f"{self.cafe_name} ({self.location.location_name})"


class Drink(models.Model):
    drink_id = models.AutoField(primary_key=True)
    drink_name = models.CharField("Название напитка", max_length=100, unique=True)
    price = models.DecimalField(
        "Цена за порцию",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Напиток"
        verbose_name_plural = "Меню напитков"
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=Decimal("0.00")),
                name="drink_price_positive",
            ),
        ]

    def __str__(self):
        return f"{self.drink_name}"


class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    last_name = models.CharField("Фамилия", max_length=60)
    first_name = models.CharField("Имя", max_length=60)
    middle_name = models.CharField("Отчество", max_length=60, null=True, blank=True)
    phone_number = models.CharField("Номер телефона", max_length=25, unique=True)
    registration_date = models.DateField("Дата регистрации", default=timezone.localdate)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}"
        if self.middle_name:
            full_name += f" {self.middle_name}"
        return full_name


class SkiPass(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Активен"
        BLOCKED = "blocked", "Заблокирован"

    ski_pass_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="ski_passes",
        verbose_name="Клиент",
    )
    card_number = models.CharField("Номер карты", max_length=25, unique=True)
    balance = models.DecimalField(
        "Баланс",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        verbose_name = "Ски-пасс"
        verbose_name_plural = "Ски-пассы"
        constraints = [
            models.CheckConstraint(
                condition=Q(balance__gte=Decimal("0.00")),
                name="ski_pass_balance_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(status__in=["active", "blocked"]),
                name="ski_pass_valid_status",
            ),
        ]

    def __str__(self):
        return f"{self.card_number}"


class BalanceOperation(models.Model):
    operation_id = models.AutoField(primary_key=True)
    ski_pass = models.ForeignKey(
        SkiPass,
        on_delete=models.CASCADE,
        related_name="balance_operations",
        verbose_name="Ски-пасс",
    )
    amount = models.DecimalField(
        "Сумма операции",
        max_digits=10,
        decimal_places=2,
    )
    operation_datetime = models.DateTimeField(
        "Дата и время операции",
        default=timezone.now,
    )

    class Meta:
        verbose_name = "Операция с балансом"
        verbose_name_plural = "Операции с балансом"
        constraints = [
            models.CheckConstraint(
                condition=~Q(amount=Decimal("0.00")),
                name="balance_operation_amount_non_zero",
            ),
        ]

    def __str__(self):
        if self.amount > 0:
            return f"{self.ski_pass.card_number} Пополнение "
        return f"{self.ski_pass.card_number} Списание"


class PassLog(models.Model):
    class Result(models.TextChoices):
        SUCCESS = "success", "Успешно"
        DENIED = "denied", "Отказ"

    pass_log_id = models.AutoField(primary_key=True)
    ski_pass = models.ForeignKey(
        SkiPass,
        on_delete=models.CASCADE,
        related_name="pass_logs",
        verbose_name="Ски-пасс",
    )
    turnstile = models.ForeignKey(
        Turnstile,
        on_delete=models.PROTECT,
        related_name="pass_logs",
        verbose_name="Турникет",
    )
    pass_datetime = models.DateTimeField("Дата и время прохода", default=timezone.now)
    charged_amount = models.DecimalField(
        "Списанная сумма",
        max_digits=10,
        decimal_places=2,
    )
    result = models.CharField(
        "Результат",
        max_length=20,
        choices=Result.choices,
    )

    class Meta:
        verbose_name = "Запись прохода"
        verbose_name_plural = "Журнал проходов"
        constraints = [
            models.CheckConstraint(
                condition=Q(charged_amount__gte=Decimal("0.00")),
                name="pass_log_charged_amount_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(result__in=["success", "denied"]),
                name="pass_log_valid_result",
            ),
            models.CheckConstraint(
                condition=~Q(result="denied") | Q(charged_amount=Decimal("0.00")),
                name="pass_log_denied_zero_charge",
            ),
        ]

    def __str__(self):
        return f"{self.ski_pass.card_number} > {self.turnstile.turnstile_name}"


class DrinkPurchase(models.Model):
    purchase_id = models.AutoField(primary_key=True)
    ski_pass = models.ForeignKey(
        SkiPass,
        on_delete=models.CASCADE,
        related_name="drink_purchases",
        verbose_name="Ски-пасс",
    )
    sale_point = models.ForeignKey(
        SalePoint,
        on_delete=models.PROTECT,
        related_name="drink_purchases",
        verbose_name="Точка продажи",
    )
    drink = models.ForeignKey(
        Drink,
        on_delete=models.PROTECT,
        related_name="purchases",
        verbose_name="Напиток",
    )
    purchase_datetime = models.DateTimeField(
        "Дата и время покупки", default=timezone.now
    )
    quantity = models.SmallIntegerField("Количество порций")
    charged_amount = models.DecimalField(
        "Итоговая сумма",
        max_digits=10,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Покупка напитка"
        verbose_name_plural = "Покупки напитков"
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0),
                name="drink_purchase_quantity_positive",
            ),
            models.CheckConstraint(
                condition=Q(charged_amount__gt=Decimal("0.00")),
                name="drink_purchase_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.drink.drink_name} x{self.quantity} ({self.ski_pass.card_number})"
