from django.http import HttpResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db.utils import IntegrityError
from django_pandas.io import read_frame
from django.db.models import Sum

from .serializers import *
from .models import *
from datetime import datetime

import pandas as pd
import io


@api_view(['POST'])
@parser_classes((JSONParser,))
def employee_registration(request):
    print(request.data)
    try:
        employee = Employee.objects.create(
            fio=request.data["fio"],
            activity_direction=ActivityDirection.objects.get(pk=request.data["activity_direction"]),
            vats_number=request.data["vats_number"],
            login=request.data["login"],
            password=request.data["password"],
            contract_agree=request.data["contract_agree"]
        )
        return Response({"status": True, "object": EmployeeSerializer(employee, many=False).data})
    except IntegrityError as e:
        return Response({"status": False,
                         "error": "Cannot register a new employee! Employee with this login is already exist!",
                         "detail": str(e)})
    except ActivityDirection.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Cannot register a new employee! Declared activity direction doesn't exist!",
                         "detail": str(e)})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Cannot register a new employee! Some field is wrong! "
                                  "Needed fields is "
                                  "(fio: String, "
                                  "activity_direction: Integer, "
                                  "vats_number: String, "
                                  "login: String, "
                                  "password: String, "
                                  "contract_agree: bool)",
                         "detail": str(e)})


@api_view(['POST'])
@parser_classes((JSONParser,))
def employee_authorization(request):
    try:
        return Response({"status": True,
                         "object": EmployeeSerializer(Employee.objects.get(login=request.data["login"],
                                                                           password=request.data["password"]
                                                                           ), many=False).data})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Key error!!! Needed fields is "
                                  "(login: String, "
                                  "password: String )",
                         "detail": str(e)})
    except Employee.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Login or password is wrong!",
                         "detail": str(e)})


@api_view(['GET', 'POST'])
def get_activity_directions(request):
    return Response(ActivityDirectionSerializer(ActivityDirection.objects.all(), many=True).data)


@api_view(['GET', 'POST'])
def get_price_list(request):
    return Response(PriceListSerializer(PriceList.objects.all(), many=True).data)


@api_view(['POST'])
@parser_classes((JSONParser,))
def new_order(request):
    try:
        order = Orders.objects.create(
            employee=Employee.objects.get(pk=request.data["employee_id"]),
            client_number=request.data["client_phone"],
            order_price=request.data["order_price"]
        )
        try:
            order.payed = request.data["payed"]
            order.save()
        except KeyError:
            pass
        return Response({"status": True,
                         "object": OrderSerializer(order, many=False).data})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Key error!!! Needed fields is "
                                  "(employee_id: Integer, "
                                  "client_phone: String, "
                                  "order_price: Double)",
                         "detail": str(e)})
    except Employee.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Wrong employee id!",
                         "detail": str(e)})


@api_view(["POST"])
@parser_classes((JSONParser,))
def employee_statistics(request):
    try:
        now = datetime.now()
        employee = Employee.objects.get(pk=request.data["employee_id"])
        calls = Calls.objects.filter(employee=employee, date__month=now.month, date__year=now.year).aggregate(
            Sum('count')
        )["count__sum"]
        orders = Orders.objects.filter(employee=employee, date__year=now.year, date__month=now.month).count()
        try:
            planed = EmployeeAdminSettings.objects.get(employee=employee)
            rating = planed.rating
            planed = planed.planned_num_of_orders
        except EmployeeAdminSettings.DoesNotExist:
            planed = 0
            rating = 0.0
        return Response({
            "status": True,
            "calls": calls,
            "orders": orders,
            "planed": planed,
            "rating": rating
        })
    except Employee.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Wrong employee id!",
                         "detail": str(e)})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Key error!!! Needed fields is "
                                  "(employee_id: Integer)",
                         "detail": str(e)})


@api_view(["POST"])
@parser_classes((JSONParser,))
def increase_calls(request):
    try:
        employee = Employee.objects.get(pk=request.data["employee_id"])
        updated_calls = Calls.increase_or_add(employee=employee, count=request.data["count"])
        return Response({"status": True,
                         "object": CallSerializer(updated_calls, many=False).data})
    except Employee.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Wrong employee id!",
                         "detail": str(e)})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Key error!!! Needed fields is "
                                  "(employee_id: Integer, "
                                  "count: Integer )",
                         "detail": str(e)})


def get_excel_statistic(request):
    excel_file = io.BytesIO()
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    row = 1
    y_bold = writer.book.add_format({'bold': True, 'bg_color': 'yellow'})
    ws = writer.book.add_worksheet("Парнёри")
    ws.write(0, 0, "ID", y_bold)
    ws.write(0, 1, "Логин", y_bold)
    ws.write(0, 2, "ФИО", y_bold)
    ws.write(0, 3, "Направление деятильности", y_bold)
    ws.write(0, 4, "Номер ВАТС", y_bold)
    ws.write(0, 5, "Подверждение договора", y_bold)
    ws.write(0, 6, "Дата договора", y_bold)
    ws.write(0, 7, "К-во запланированих заказов в месяц", y_bold)
    ws.write(0, 8, "Рейтинг", y_bold)
    for employee in Employee.objects.all():
        ws.write(row, 0, employee.pk)
        ws.write(row, 1, employee.login)
        ws.write(row, 2, employee.fio)
        ws.write(row, 3, employee.activity_direction.name)
        ws.write(row, 4, employee.vats_number)
        ws.write(row, 5, employee.contract_agree)
        ws.write(row, 6, employee.contract_date.strftime("%x"))
        try:
            plan = EmployeeAdminSettings.objects.get(employee=employee)
            ws.write(row, 6, plan.planned_num_of_orders)
            ws.write(row, 7, plan.rating)
        except EmployeeAdminSettings.DoesNotExist:
            pass
        row += 1
    row = 1
    ws = writer.book.add_worksheet("Дзвонки")
    ws.write(0, 0, "Дата", y_bold)
    ws.write(0, 1, "ID-Пернёра", y_bold)
    ws.write(0, 2, "ФИО", y_bold)
    ws.write(0, 3, "К-во", y_bold)
    for call in Calls.objects.all():
        ws.write(row, 0, call.date.strftime("%x"))
        ws.write(row, 1, call.employee_id)
        ws.write(row, 2, call.employee.fio)
        ws.write(row, 3, call.count)
        row += 1
    row = 1
    ws = writer.book.add_worksheet("Клиенты")
    ws.write(0, 0, "ID", y_bold)
    ws.write(0, 1, "ФИО", y_bold)
    ws.write(0, 2, "Номер телефона", y_bold)
    ws.write(0, 3, "Дата регистрации", y_bold)
    for client in Clients.objects.all():
        ws.write(row, 0, client.pk)
        ws.write(row, 1, client.fio)
        ws.write(row, 2, client.phone_number)
        ws.write(row, 3, client.registration_date_time.strftime("%x %X"))
        row += 1
    row = 1
    ws = writer.book.add_worksheet("Направления деятельности")
    ws.write(0, 0, "ID", y_bold)
    ws.write(0, 1, "Направление", y_bold)
    ws.write(0, 2, "Описание", y_bold)
    for activity_direction in ActivityDirection.objects.all():
        ws.write(row, 0, activity_direction.pk)
        ws.write(row, 1, activity_direction.name)
        ws.write(row, 2, activity_direction.description)
        row += 1

    writer.save()
    writer.close()

    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % str(datetime.now().strftime("%x__%X"))
    return response


@api_view(["POST"])
@parser_classes((JSONParser,))
def get_or_change_employee_status(request):
    try:
        response = {"status": True}
        employee = Employee.objects.get(pk=request.data["employee_id"])
        try:
            status = request.data["employee_status"]
            employee.status = status
            employee.save()
        except KeyError:
            pass
        response["current_employee_status"] = employee.status
        return Response(response)
    except Employee.DoesNotExist as e:
        return Response({"status": False,
                         "error": "Wrong employee id!",
                         "detail": str(e)})
    except KeyError as e:
        return Response({"status": False,
                         "error": "Key error!!! Needed fields is "
                                  "(employee_id: Integer, "
                                  "employee_status: Boolean ) for Change or just (employee_id: Integer) for Get.",
                         "detail": str(e)})


def rating_generation():
    now = datetime.now()
    result = []
    order_stat = Orders \
        .objects \
        .filter(date__year=now.year, date__month=now.month) \
        .values("employee") \
        .annotate(count=Count("*"), total_price=Sum("order_price"))
    all_calls_count = Calls.objects.filter(
        date__year=now.year,
        date__month=now.month
    ).aggregate(Sum("count"))["count__sum"]
    all_calls_count = all_calls_count if all_calls_count is not None or all_calls_count is not 0 else 1
    for employee in Employee.objects.all():
        current_employee_calls_count = Calls.objects.filter(
            pk=employee.pk,
            date__year=now.year,
            date__month=now.month
        ).aggregate(Sum("count"))["count__sum"]
        current_employee_calls_count = current_employee_calls_count if current_employee_calls_count is not None else 0
        statistic_item = {
            "employee_id": employee.pk,
            "fio": employee.fio,
            "total_calls": current_employee_calls_count,
            "calls_in_percent": (current_employee_calls_count/all_calls_count * 100)
        }
        try:
            order_stat_item = order_stat.get(employee=employee)
            statistic_item["total_price"] = order_stat_item["total_price"]
            statistic_item["orders_count"] = order_stat_item["count"]
        except Orders.DoesNotExist:
            statistic_item["total_price"] = 0.0
            statistic_item["orders_count"] = 0
        result.append(statistic_item)
    return sorted(result, key=lambda k: k["total_price"], reverse=True)


@api_view(["GET", "POST"])
def get_employees_rating(request):
    return Response(rating_generation())


@api_view(["GET", "POST"])
def get_information(request):
    return Response(InformationSerializer(Information.objects.all(), many=True).data)


@api_view(["POST"])
@parser_classes((JSONParser,))
def get_order_history(request):
    try:
        now = datetime.now()
        orders = Orders.objects.filter(
            employee_id=request.data["employee_id"],
            date__year=now.year,
            date__month=now.month
        )
        return Response({
            "status": True,
            "orders": OrderSerializer(orders, many=True).data
        })
    except KeyError as e:
        return Response({
            "status": False,
            "error": "Key error: missing "+str(e)
        })




