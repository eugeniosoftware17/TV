from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    from django.conf import settings

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    UserProfile = apps.get_model("accounts", "UserProfile")
    for user in User.objects.all():
        if not UserProfile.objects.filter(user=user).exists():
            role = "admin" if getattr(user, "is_superuser", False) else "viewer"
            UserProfile.objects.create(user=user, role=role)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, migrations.RunPython.noop),
    ]
