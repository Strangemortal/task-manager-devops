from django.db import migrations


def create_superuser(apps, schema_editor):
    User = apps.get_model("main", "User")
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123",
            role="admin",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
