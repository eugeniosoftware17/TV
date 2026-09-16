import presentations.models
from django.db import migrations, models


def reassign_tokens(apps, schema_editor):
    """Reasigna códigos numéricos de 3 dígitos (001-999) a presentaciones existentes."""
    Presentation = apps.get_model("presentations", "Presentation")
    queryset = Presentation.objects.order_by("pk")
    if queryset.count() > 999:
        raise ValueError(
            "No hay códigos de presentación disponibles (más de 999 presentaciones existentes)."
        )
    for index, presentation in enumerate(queryset, start=1):
        presentation.token = f"{index:03d}"
        presentation.save(update_fields=["token"])


class Migration(migrations.Migration):

    dependencies = [
        ("presentations", "0002_mediaasset_is_processed_presentation_source_type_and_more"),
    ]

    operations = [
        migrations.RunPython(reassign_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="presentation",
            name="token",
            field=models.CharField(
                default=presentations.models.generate_presentation_token,
                editable=False,
                max_length=3,
                unique=True,
            ),
        ),
    ]
