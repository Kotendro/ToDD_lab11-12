import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from main.models import (
    BalanceOperation,
    Client,
    Drink,
    DrinkPurchase,
    Location,
    PassLog,
    SalePoint,
    SkiPass,
    Turnstile,
)


class Command(BaseCommand):
    help = "Генерация тестовых записей"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить таблицы перед заполнением",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker("ru_RU")

        if options["clear"]:
            self.stdout.write("Очистка старых данных...")
            DrinkPurchase.objects.all().delete()
            PassLog.objects.all().delete()
            BalanceOperation.objects.all().delete()
            SkiPass.objects.all().delete()
            Client.objects.all().delete()
            Turnstile.objects.all().delete()
            SalePoint.objects.all().delete()
            Drink.objects.all().delete()
            Location.objects.all().delete() 
 
        # 1. Справочники (Локации, Турникеты, Кафе, Напитки)
        locations = [
            Location.objects.get_or_create(location_name=name)[0]
            for name in [
                "Южный склон",
                "Северный склон",
                "Нижняя станция",
                "Учебный склон",
                "Пик 2200",
            ]
        ]

        turnstiles = []
        for i, loc in enumerate(locations, start=1):
            for j in range(1, 3):
                t, _ = Turnstile.objects.get_or_create(
                    location=loc,
                    turnstile_name=f"Турникет {i}-{j}",
                    defaults={
                        "pass_price": Decimal(
                            random.choice(["250.00", "350.00", "500.00"])
                        )
                    },
                )
                turnstiles.append(t)

        sale_points = []
        for i, loc in enumerate(locations, start=1):
            sp, _ = SalePoint.objects.get_or_create(
                location=loc,
                cafe_name=f"Кафе «Снежинка #{i}»",
                defaults={"open_time": "09:00", "close_time": "21:00"},
            )
            sale_points.append(sp)

        drinks_data = [
            ("Глинтвейн безалкогольный", "250.00"),
            ("Горячий шоколад", "220.00"),
            ("Облепиховый чай", "190.00"),
            ("Капучино", "210.00"),
            ("Американо", "160.00"),
            ("Имбирный пунш", "240.00"),
        ]
        drinks = [
            Drink.objects.get_or_create(
                drink_name=name, defaults={"price": Decimal(price)}
            )[0]
            for name, price in drinks_data
        ]

        # 2. Генерируем 350 клиентов
        self.stdout.write("Генерация клиентов...")
        clients_batch = []
        used_phones = set(Client.objects.values_list("phone_number", flat=True))

        while len(clients_batch) < 350:
            phone = f"+79{random.randint(100000000, 999999999)}"
            if phone in used_phones:
                continue
            used_phones.add(phone)

            is_male = random.choice([True, False])
            clients_batch.append(
                Client(
                    last_name=fake.last_name_male()
                    if is_male
                    else fake.last_name_female(),
                    first_name=fake.first_name_male()
                    if is_male
                    else fake.first_name_female(),
                    middle_name=(
                        fake.middle_name_male()
                        if is_male
                        else fake.middle_name_female()
                    )
                    if random.random() > 0.15
                    else None,  # 15% без отчества
                    phone_number=phone,
                    registration_date=fake.date_between(
                        start_date="-2y", end_date="today"
                    ),
                )
            )

        clients = Client.objects.bulk_create(clients_batch)

        # 3. Генерируем 400 ски-пассов (у некоторых клиентов по 2 карты)
        self.stdout.write("Генерация ски-пассов...")
        passes_batch = []
        used_cards = set(SkiPass.objects.values_list("card_number", flat=True))

        for i in range(400):
            client = clients[i] if i < len(clients) else random.choice(clients)
            while True:
                card_num = f"SP-{random.randint(100000, 999999)}"
                if card_num not in used_cards:
                    used_cards.add(card_num)
                    break

            passes_batch.append(
                SkiPass(
                    client=client,
                    card_number=card_num,
                    balance=Decimal(random.randint(0, 15000)),
                    status=SkiPass.Status.ACTIVE
                    if random.random() > 0.1
                    else SkiPass.Status.BLOCKED,
                )
            )

        ski_passes = SkiPass.objects.bulk_create(passes_batch)

        # 4. Операции с балансом
        self.stdout.write("Генерация операций и журналов...")
        now = timezone.now()
        ops_batch = []
        for _ in range(800):
            is_topup = random.random() > 0.15
            amount = Decimal(random.choice([500, 1000, 2000, 3000, 5000]))
            if not is_topup:
                amount = -amount

            ops_batch.append(
                BalanceOperation(
                    ski_pass=random.choice(ski_passes),
                    amount=amount,
                    operation_datetime=now
                    - timedelta(
                        days=random.randint(0, 60), minutes=random.randint(0, 1440)
                    ),
                )
            )
        BalanceOperation.objects.bulk_create(ops_batch)

        # 5. Журнал проходов
        logs_batch = []
        for _ in range(1200):
            turnstile = random.choice(turnstiles)
            is_success = random.random() > 0.12
            logs_batch.append(
                PassLog(
                    ski_pass=random.choice(ski_passes),
                    turnstile=turnstile,
                    pass_datetime=now
                    - timedelta(
                        days=random.randint(0, 60), minutes=random.randint(0, 1440)
                    ),
                    charged_amount=turnstile.pass_price
                    if is_success
                    else Decimal("0.00"),
                    result=PassLog.Result.SUCCESS
                    if is_success
                    else PassLog.Result.DENIED,
                )
            )
        PassLog.objects.bulk_create(logs_batch)

        # 6. Покупки напитков
        purchases_batch = []
        for _ in range(600):
            drink = random.choice(drinks)
            qty = random.randint(1, 4)
            purchases_batch.append(
                DrinkPurchase(
                    ski_pass=random.choice(ski_passes),
                    sale_point=random.choice(sale_points),
                    drink=drink,
                    purchase_datetime=now
                    - timedelta(
                        days=random.randint(0, 60), minutes=random.randint(0, 1440)
                    ),
                    quantity=qty,
                    charged_amount=drink.price * qty,
                )
            )
        DrinkPurchase.objects.bulk_create(purchases_batch)

        # 7. Тестовые пользователи
        self.stdout.write("Создание пользователей...")
        from django.contrib.auth import get_user_model

        User = get_user_model()

        users_data = [
            ("user", "user", {"is_staff": False, "is_superuser": False}),
            ("staff", "staff", {"is_staff": True, "is_superuser": False}),
            ("admin", "admin", {"is_staff": True, "is_superuser": True}),
        ]

        for username, password, flags in users_data:
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)  # хеширует, а не хранит в открытом виде
            user.is_staff = flags["is_staff"]
            user.is_superuser = flags["is_superuser"]
            user.is_active = True
            user.save()
            status = "создан" if created else "обновлён"
            self.stdout.write(f"  {username} ({status})")


        self.stdout.write(
            self.style.SUCCESS(
                f"Готово! Создано: {len(clients)} клиентов, {len(ski_passes)} ски-пассов, "
                f"{len(ops_batch)} операций, {len(logs_batch)} проходов, {len(purchases_batch)} покупок. "
                f"Пользователи: user/user, staff/staff, admin/admin."
            )
        )
