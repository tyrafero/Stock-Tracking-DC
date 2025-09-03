# Generated manually to fix missing location field
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0029_auto_20250902_0652'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='location',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]