# Generated by Django 4.2.6 on 2023-10-16 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opening',
            fields=[
                ('id', models.CharField(db_index=True, max_length=25, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('deadline', models.DateTimeField()),
                ('notifications', models.JSONField(blank=True, default=list, null=True)),
                ('role', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(db_index=True, max_length=25)),
                ('email', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('user_type', models.CharField(choices=[('admin', 'Admin'), ('student', 'Student'), ('s_admin', 'Super Admin')], max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'User',
                'ordering': ['created_at'],
                'unique_together': {('email', 'id')},
            },
        ),
        migrations.CreateModel(
            name='FCMToken',
            fields=[
                ('token', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='FirebasePushApi.user')),
            ],
            options={
                'verbose_name_plural': 'FCMToken',
                'ordering': ['created_at'],
            },
        ),
    ]