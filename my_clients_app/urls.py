from django.urls import path
from . import views

app_name = "my_clients_app"

urlpatterns = [
    path('get/activity_directions/', views.get_activity_directions),
    path('get/price_list/', views.get_price_list),
    path('get/information/', views.get_information),
    path('get/employees/rating/', views.get_employees_rating),
    path('employee/registration/', views.employee_registration),
    path('employee/authorization/', views.employee_authorization),
    path('employee/new/order/', views.new_order),
    path('employee/get/statistics/', views.employee_statistics),
    path('employee/get/order/history/', views.get_order_history),
    path('employee/get_or_update/status/', views.get_or_change_employee_status),
    path('employee/update/call/count/', views.increase_calls),
    path('statistic/excel/', views.get_excel_statistic, name="excel"),
]
