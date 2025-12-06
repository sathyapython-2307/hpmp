from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VitalSign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heart_rate', models.PositiveIntegerField(help_text='BPM')),
                ('systolic_bp', models.PositiveIntegerField(help_text='mmHg')),
                ('diastolic_bp', models.PositiveIntegerField(help_text='mmHg')),
                ('temperature', models.DecimalField(decimal_places=1, help_text='°F', max_digits=4)),
                ('spo2', models.PositiveIntegerField(help_text='%')),
                ('glucose', models.PositiveIntegerField(blank=True, help_text='mg/dL', null=True)),
                ('respiration_rate', models.PositiveIntegerField(blank=True, help_text='breaths/min', null=True)),
                ('notes', models.TextField(blank=True)),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vital_signs', to='patients.patient')),
                ('recorded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='VitalAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameter', models.CharField(max_length=50)),
                ('value', models.CharField(max_length=50)),
                ('normal_range', models.CharField(max_length=50)),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20)),
                ('message', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vital_alerts', to='patients.patient')),
                ('resolved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_alerts', to='accounts.user')),
                ('vital_sign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='vitals.vitalsign')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
