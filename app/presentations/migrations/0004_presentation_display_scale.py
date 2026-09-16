from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("presentations", "0003_alter_presentation_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="presentation",
            name="display_scale",
            field=models.IntegerField(
                choices=[(65, "65%"), (75, "75%"), (85, "85%"), (95, "95%"), (100, "100%")],
                default=100,
                verbose_name="Escala de pantalla",
            ),
        ),
    ]
