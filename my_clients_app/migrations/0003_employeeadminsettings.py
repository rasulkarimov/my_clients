# Generated by Django 2.0.6 on 2018-08-09 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_clients_app', '0002_auto_20180808_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeAdminSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('planned_num_of_orders', models.IntegerField(default=0, verbose_name='К-во запланированих заказов')),
                ('employees', models.ManyToManyField(to='my_clients_app.Employee', verbose_name='Работники')),
            ],
        ),
    ]