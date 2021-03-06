# Generated by Django 3.2.11 on 2022-02-05 18:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created_at')),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='updated_at')),
                ('url', models.URLField(help_text='Page url given by the user to be scraped.')),
                ('title', models.CharField(blank=True, help_text='Feed page title.', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Feed page description.')),
                ('image', models.ImageField(blank=True, help_text='Feed page image', null=True, upload_to='')),
                ('auto_update_is_active', models.BooleanField(default=True, help_text='Determines whether the feed content will be automatically updated in the background periodically.')),
                ('is_followed', models.BooleanField(default=True, help_text='Does this feed followed by the user? so its content will updated and (s)he will be notified.')),
                ('last_update_by_source_at', models.DateTimeField(blank=True, help_text='When was the last time this feed updated by the source site.', null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='feeds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-updated_at',),
                'unique_together': {('url', 'user')},
            },
        ),
    ]
