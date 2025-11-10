# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("followupper", "0012_contact_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="messagetemplate",
            name="footer",
            field=models.TextField(blank=True, help_text="Footer/signature for emails only"),
        ),
    ]

