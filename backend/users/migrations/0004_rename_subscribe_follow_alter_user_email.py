# Generated by Django 4.1.7 on 2023-03-05 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_delete_follow'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subscribe',
            new_name='Follow',
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
    ]