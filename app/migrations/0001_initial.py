# Generated by Django 4.0.6 on 2022-07-30 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Queue",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=100, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                "db_table": "queue",
            },
        ),
        migrations.CreateModel(
            name="Subreddit",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=100, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("subscribers", models.IntegerField()),
                ("type", models.TextField()),
            ],
            options={
                "db_table": "subreddits",
            },
        ),
        migrations.CreateModel(
            name="Relation",
            fields=[
                (
                    "id",
                    models.CharField(
                        max_length=100, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("type", models.CharField(max_length=100)),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="sources",
                        to="app.subreddit",
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="targets",
                        to="app.subreddit",
                    ),
                ),
            ],
            options={
                "db_table": "relations",
            },
        ),
    ]