from django.db import migrations,models
import django.db.models.deletion
from django.conf import settings
class Migration(migrations.Migration):
    initial=True
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[
        migrations.CreateModel(name='Autor',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('nombre',models.CharField(max_length=120)),('nacionalidad',models.CharField(blank=True,max_length=80)),('biografia',models.TextField(blank=True))]),
        migrations.CreateModel(name='Libro',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('isbn',models.CharField(max_length=20,unique=True)),('titulo',models.CharField(max_length=180)),('editorial',models.CharField(blank=True,max_length=120)),('anio',models.PositiveIntegerField()),('categoria',models.CharField(max_length=80)),('stock',models.PositiveIntegerField(default=0)),('ubicacion',models.CharField(blank=True,max_length=80)),('autor',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='libros',to='biblioteca.autor'))]),
        migrations.CreateModel(name='Prestamo',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('fecha_prestamo',models.DateField(auto_now_add=True)),('fecha_devolucion',models.DateField()),('estado',models.CharField(choices=[('activo','Activo'),('devuelto','Devuelto'),('vencido','Vencido')],default='activo',max_length=10)),('libro',models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,related_name='prestamos',to='biblioteca.libro')),('usuario',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='prestamos',to=settings.AUTH_USER_MODEL))])]
