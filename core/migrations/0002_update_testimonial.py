from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testimonial',
            old_name='content',
            new_name='message',
        ),
        migrations.RenameField(
            model_name='testimonial',
            old_name='position',
            new_name='role',
        ),
        migrations.AddField(
            model_name='testimonial',
            name='company',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RenameField(
            model_name='testimonial',
            old_name='is_active',
            new_name='is_approved',
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='rating',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=5),
        ),
        migrations.AlterModelOptions(
            name='testimonial',
            options={'ordering': ['-created_at']},
        ),
    ]
