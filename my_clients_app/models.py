from django.db import models
from datetime import datetime


class ActivityDirection(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Направления деятельности"
        verbose_name = "направление деятельности"


class Employee(models.Model):
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    contract_date = models.DateField(auto_now_add=True, verbose_name="Дата договора")
    activity_direction = models.ForeignKey(ActivityDirection, on_delete=models.SET_NULL,
                                           verbose_name="Направление деятельности", null=True)
    vats_number = models.CharField(max_length=20, verbose_name="Номер ВАТС")
    login = models.CharField(max_length=30, verbose_name="Логин", unique=True)
    password = models.CharField(max_length=30, verbose_name="Пароль")
    contract_agree = models.BooleanField(default=False, verbose_name="Подтверждение договора")
    status = models.BooleanField(default=True, verbose_name="Требуются ли клиенты")

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name_plural = "Партнёры"
        verbose_name = "парнёр"


class PriceList(models.Model):
    min_price = models.PositiveIntegerField(verbose_name="Минимальное значение", default=0)
    max_price = models.PositiveIntegerField(verbose_name="Максимальное значение", default=0)
    prc_commission = models.SmallIntegerField(verbose_name="%")
    max_commission = models.PositiveIntegerField(verbose_name="Но не более", default=0)

    class Meta:
        verbose_name_plural = "Комиссионное вознаграждение"
        verbose_name = "комиссионное вознаграждение"

    def __str__(self):
        return str(self.min_price)+"-"+str(self.max_price)+" | "+str(self.prc_commission)+"% | "+str(self.max_commission)


class EmployeeAdminSettings(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, verbose_name="Партнёр")
    planned_num_of_orders = models.IntegerField(default=0, verbose_name="К-во запланированих заказов")
    rating = models.FloatField(default=0.0, verbose_name="Рейтинг")

    def __str__(self):
        return self.employee.fio

    class Meta:
        verbose_name_plural = "Планы заказов"
        verbose_name = "план заказов"


class Clients(models.Model):
    fio = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона", unique=True)
    registration_date_time = models.DateTimeField(auto_now=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name_plural = "Клиенты"
        verbose_name = "клиент"

    def __str__(self):
        return self.fio+" ("+self.phone_number+")"



class Orders(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Партнёр", null=True)
    client_number = models.CharField(max_length=20, verbose_name="Номер клиента")
    order_price = models.FloatField(verbose_name="Цена заявки")
    payed = models.FloatField(verbose_name="Оплачено", default=0.0)
    checking_act = models.CharField(verbose_name="Акт сверки", max_length=300, default="")
    rejecting = models.IntegerField(verbose_name="Отклонения", default=0)
    date = models.DateField(verbose_name="Дата заказа", auto_now_add=True)
    time = models.TimeField(verbose_name="Время заказа", auto_now_add=True)

    class Meta:
        verbose_name_plural = "Заявки"
        verbose_name = "заявка"

    def __str__(self):
        return "Заказ №"+str(self.pk)+" Партнёр ("+self.employee.fio+") Номер клиента ("+self.client_number+")"


class Calls(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Партнёр", null=True)
    count = models.IntegerField(verbose_name="К-во звонков", default=0)
    date = models.DateField(verbose_name="Дата", auto_now=True)

    class Meta:
        verbose_name_plural = "Дзвонки клиентов"
        verbose_name = "дзвонки клиента"

    def __str__(self):
        return "Дата ("+str(self.date)+") Партнёр ("+self.employee.fio+") К-во ("+str(self.count)+")"

    @staticmethod
    def increase_or_add(employee: Employee, count: int):
        try:
            calls = Calls.objects.get(employee_id=employee.id, date=datetime.today())
            calls.count += count
            calls.save()
            return calls
        except Calls.DoesNotExist:
            return Calls.objects.create(employee=employee, count=count)


class Information(models.Model):
    question = models.TextField(verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")

    class Meta:
        verbose_name_plural = "Информация"
        verbose_name = "информация"

    def __str__(self):
        length = len(self.question)
        return self.question[:20 if length > 20 else length]+"..."

