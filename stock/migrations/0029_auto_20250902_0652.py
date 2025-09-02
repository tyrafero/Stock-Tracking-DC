# Generated manually on 2025-09-02 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0028_stockaudit_stockaudititem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseorder',
            name='store',
            field=models.ForeignKey(
                blank=False, 
                null=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to='stock.store',
                help_text='Delivery location where items will be received and added to inventory',
                verbose_name='Delivery Location'
            ),
        ),
    ]