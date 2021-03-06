# Generated by Django 2.2 on 2020-02-20 06:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('transaction', '0024_auto_20200217_1300'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salereturnheader',
            name='follow_up',
        ),
        migrations.AddField(
            model_name='salereturndetail',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=14),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salereturnheader',
            name='account_holder',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salereturnheader',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=14),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='salereturnheader',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='height',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='rate',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='total_pcs',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='total_square_fit',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
        migrations.AlterField(
            model_name='salereturndetail',
            name='width',
            field=models.DecimalField(decimal_places=2, max_digits=14),
        ),
    ]
