from django.conf import settings
from django.db import models
class Autor(models.Model):
    nombre=models.CharField(max_length=120); nacionalidad=models.CharField(max_length=80,blank=True); biografia=models.TextField(blank=True)
    def __str__(self): return self.nombre
class Libro(models.Model):
    isbn=models.CharField(max_length=20,unique=True); titulo=models.CharField(max_length=180); autor=models.ForeignKey(Autor,on_delete=models.PROTECT,related_name='libros'); editorial=models.CharField(max_length=120,blank=True); anio=models.PositiveIntegerField(); categoria=models.CharField(max_length=80); stock=models.PositiveIntegerField(default=0); ubicacion=models.CharField(max_length=80,blank=True)
    @property
    def disponible(self): return self.stock>0
    def __str__(self): return self.titulo
class Prestamo(models.Model):
    ESTADOS=[('activo','Activo'),('devuelto','Devuelto'),('vencido','Vencido')]
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='prestamos'); libro=models.ForeignKey(Libro,on_delete=models.PROTECT,related_name='prestamos'); fecha_prestamo=models.DateField(auto_now_add=True); fecha_devolucion=models.DateField(); estado=models.CharField(max_length=10,choices=ESTADOS,default='activo')
    def __str__(self): return f'{self.usuario} - {self.libro}'
