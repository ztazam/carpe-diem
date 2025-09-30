from django.db import migrations

def update_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site = Site.objects.get(id=1)
    site.domain = 'carpe-diem-v4dd.onrender.com'
    site.name = 'CarpeDiem'
    site.save()

def reverse_update(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    site = Site.objects.get(id=1)
    site.domain = 'example.com'
    site.name = 'example.com'
    site.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_perfilusuario_is_premium_perfilusuario_premium_since_and_more'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(update_site, reverse_update),
    ]