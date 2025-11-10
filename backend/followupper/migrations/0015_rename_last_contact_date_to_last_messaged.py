# Generated migration to rename last_contact_date to last_messaged

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('followupper', '0014_userprofile'),
    ]

    operations = [
        # Rename the field
        migrations.RenameField(
            model_name='contact',
            old_name='last_contact_date',
            new_name='last_messaged',
        ),
        # Update the field definition to match the new model
        migrations.AlterField(
            model_name='contact',
            name='last_messaged',
            field=models.DateTimeField(blank=True, db_index=True, help_text='Date and time of the most recent sent message', null=True),
        ),
    ]
