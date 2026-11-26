from django.conf import settings
from django.db import models
class Categoria(models.Model):
 nombre=models.CharField(max_length=100,unique=True); descripcion=models.TextField(blank=True); imagen=models.URLField(blank=True)
 def __str__(self): return self.nombre
class Vendedor(models.Model):
 usuario=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='perfil_vendedor'); nombre_tienda=models.CharField(max_length=120); slug=models.SlugField(unique=True); verificado=models.BooleanField(default=False)
 def __str__(self): return self.nombre_tienda
class Producto(models.Model):
 sku=models.CharField(max_length=40,unique=True); nombre=models.CharField(max_length=180); descripcion=models.TextField(); marca=models.CharField(max_length=100); categoria=models.ForeignKey(Categoria,on_delete=models.PROTECT,related_name='productos'); vendedor=models.ForeignKey(Vendedor,on_delete=models.CASCADE,related_name='productos'); precio=models.DecimalField(max_digits=12,decimal_places=2); descuento=models.DecimalField(max_digits=5,decimal_places=2,default=0); stock=models.PositiveIntegerField(default=0); imagenes=models.JSONField(default=list,blank=True); especificaciones=models.JSONField(default=dict,blank=True); created=models.DateTimeField(auto_now_add=True); updated=models.DateTimeField(auto_now=True)
 @property
 def precio_con_descuento(self): return self.precio*(1-self.descuento/100)
 @property
 def disponible(self): return self.stock>0
 @property
 def rating_promedio(self):
  values=self.resenas.aggregate(avg=models.Avg('calificacion'))['avg']; return round(float(values or 0),2)
 def __str__(self): return self.nombre
class Carrito(models.Model):
 usuario=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='carrito'); cupon=models.CharField(max_length=40,blank=True); updated=models.DateTimeField(auto_now=True)
 @property
 def cantidad_items(self): return sum(x.cantidad for x in self.items.all())
 @property
 def subtotal(self): return sum((x.producto.precio_con_descuento*x.cantidad for x in self.items.select_related('producto')),start=0)
 @property
 def total_con_descuento(self):
  subtotal=self.subtotal
  return subtotal*0.9 if self.cupon.upper()=='TECNO10' else subtotal
class ItemCarrito(models.Model):
 carrito=models.ForeignKey(Carrito,on_delete=models.CASCADE,related_name='items'); producto=models.ForeignKey(Producto,on_delete=models.PROTECT); cantidad=models.PositiveIntegerField(default=1)
 class Meta: unique_together=[('carrito','producto')]
 def __str__(self): return f'{self.producto} x {self.cantidad}'
class Orden(models.Model):
 ESTADOS=[('pendiente','Pendiente'),('pagada','Pagada'),('enviada','Enviada'),('entregada','Entregada'),('cancelada','Cancelada')]
 usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='ordenes'); items_snapshot=models.JSONField(default=list); direccion_envio=models.JSONField(default=dict); metodo_pago=models.CharField(max_length=40,blank=True); estado=models.CharField(max_length=12,choices=ESTADOS,default='pendiente'); subtotal=models.DecimalField(max_digits=12,decimal_places=2); total=models.DecimalField(max_digits=12,decimal_places=2); numero_seguimiento=models.CharField(max_length=32,blank=True); fecha_creacion=models.DateTimeField(auto_now_add=True)
 @property
 def entrega_estimada(self):
  from datetime import timedelta
  return self.fecha_creacion.date()+timedelta(days=5)
 def __str__(self): return f'Orden #{self.pk} - {self.usuario}'
class Resena(models.Model):
 usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='resenas'); producto=models.ForeignKey(Producto,on_delete=models.CASCADE,related_name='resenas'); calificacion=models.PositiveSmallIntegerField(); titulo=models.CharField(max_length=120); comentario=models.TextField(); fecha_creacion=models.DateTimeField(auto_now_add=True)
 class Meta: unique_together=[('usuario','producto')]
 def __str__(self): return f'{self.producto}: {self.calificacion}/5'
