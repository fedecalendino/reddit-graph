# Generated by Django 4.0.6 on 2022-08-09 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_alter_subreddit_subscribers"),
    ]

    operations = [
        migrations.AddField(
            model_name="queue",
            name="priority",
            field=models.IntegerField(default=0),
        ),
    ]