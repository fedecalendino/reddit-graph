# Generated by Django 4.0.6 on 2022-08-09 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0016_alter_subreddit_subscribers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subreddit",
            name="nsfw",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name="subreddit",
            name="quarantined",
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]