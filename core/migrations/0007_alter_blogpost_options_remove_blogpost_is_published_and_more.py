# Generated by Django 5.0.4 on 2024-12-14 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_merge_20241214_0732'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blogpost',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='blogpost',
            name='is_published',
        ),
        migrations.AddField(
            model_name='blogpost',
            name='excerpt',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=20),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='blog/'),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='testimonials/'),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
