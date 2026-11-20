from django.db import migrations


def create_profiles(apps, schema_editor):
    user_model = apps.get_model("auth", "User")
    profile_model = apps.get_model("core", "Profile")
    batch = []
    for user in user_model.objects.filter(profile__isnull=True).iterator(chunk_size=2000):
        batch.append(profile_model(user_id=user.pk, nickname=(user.first_name or user.username)[:40]))
        if len(batch) == 2000:
            profile_model.objects.bulk_create(batch, ignore_conflicts=True)
            batch = []
    profile_model.objects.bulk_create(batch, ignore_conflicts=True)


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(create_profiles, migrations.RunPython.noop)]
