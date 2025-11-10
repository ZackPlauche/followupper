# Generated migration to add user field to Contact

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('followupper', '0015_rename_last_contact_date_to_last_messaged'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='user',
            field=models.ForeignKey(
                blank=True,
                db_index=True,
                help_text='User who owns this contact',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='contacts',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

