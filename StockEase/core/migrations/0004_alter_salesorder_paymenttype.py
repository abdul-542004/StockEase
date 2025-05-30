# Generated by Django 4.2.20 on 2025-05-03 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_salesitem_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salesorder',
            name='paymentType',
            field=models.CharField(choices=[('CASH', 'Cash'), ('CHEQUE', 'Cheque'), ('BANK_TRANSFER', 'Bank Transfer'), ('MOBILE_PAYMENT', 'Mobile Payment'), ('OTHER', 'Other')], default='CASH', max_length=100),
        ),
    ]
