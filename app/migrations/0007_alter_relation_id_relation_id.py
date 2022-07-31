# Generated by Django 4.0.6 on 2022-07-30 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_alter_queue_name_alter_relation_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="relation",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddConstraint(
            model_name="relation",
            constraint=models.UniqueConstraint(
                fields=("source", "target", "type"), name="id"
            ),
        ),
    ]