from django.contrib import admin
from .models import *

admin.site.index_template = "my_clients_app/admin_index.html"
admin.site.register(ActivityDirection)
admin.site.register(EmployeeAdminSettings)
admin.site.register(PriceList)
admin.site.register(Employee)
admin.site.register(Clients)
admin.site.register(Calls)
admin.site.register(Orders)
admin.site.register(Information)

