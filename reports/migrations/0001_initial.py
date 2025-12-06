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
            name='MedicalReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('report_type', models.CharField(choices=[('lab', 'Lab Report'), ('prescription', 'Prescription'), ('scan', 'Scan Report'), ('xray', 'X-Ray'), ('mri', 'MRI'), ('ct', 'CT Scan'), ('ultrasound', 'Ultrasound'), ('ecg', 'ECG'), ('other', 'Other')], max_length=20)),
                ('file', models.FileField(upload_to='reports/')),
                ('description', models.TextField(blank=True)),
                ('report_date', models.DateField()),
                ('findings', models.TextField(blank=True)),
                ('doctor_notes', models.TextField(blank=True)),
                ('is_critical', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_reports', to='patients.patient')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={
                'ordering': ['-report_date'],
            },
        ),
    ]
