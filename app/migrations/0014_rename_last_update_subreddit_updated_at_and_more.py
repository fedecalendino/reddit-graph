# Generated by Django 4.0.6 on 2022-08-04 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0013_subreddit_img_header"),
    ]

    operations = [
        migrations.RenameField(
            model_name="subreddit",
            old_name="last_update",
            new_name="updated_at",
        ),
        migrations.AlterField(
            model_name="queue",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="relation",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name="subreddit",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
