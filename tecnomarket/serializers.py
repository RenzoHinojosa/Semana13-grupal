from decimal import Decimal
from rest_framework import serializers
from .models import Categoria,Carrito,ItemCarrito,Orden,Producto,Resena,Vendedor
class CategoriaSerializer(serializers.ModelSerializer):
 class Meta: model=Categoria; fields='__all__'
class VendedorSerializer(serializers.ModelSerializer):
 class Meta: model=Vendedor; fields=['id','nombre_tienda','slug','verificado']
class ProductoSerializer(serializers.ModelSerializer):
 categoria_detalle=CategoriaSerializer(source='categoria',read_only=True); vendedor_detalle=VendedorSerializer(source='vendedor',read_only=True); precio_con_descuento=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True); disponible=serializers.BooleanField(read_only=True); rating_promedio=serializers.FloatField(read_only=True)
 class Meta: model=Producto; fields=['id','sku','nombre','descripcion','marca','categoria','categoria_detalle','vendedor','vendedor_detalle','precio','descuento','precio_con_descuento','stock','disponible','imagenes','especificaciones','rating_promedio','created','updated']; read_only_fields=['vendedor','created','updated','rating_promedio']
 def validate(self,data):
  precio=data.get('precio',getattr(self.instance,'precio',Decimal('0'))); descuento=data.get('descuento',getattr(self.instance,'descuento',Decimal('0')))
  if precio<0: raise serializers.ValidationError({'precio':'Debe ser positivo.'})
  if not 0<=descuento<=100: raise serializers.ValidationError({'descuento':'Debe estar entre 0 y 100.'})
  return data
class ItemCarritoSerializer(serializers.ModelSerializer):
 producto_detalle=ProductoSerializer(source='producto',read_only=True); subtotal=serializers.SerializerMethodField()
 class Meta: model=ItemCarrito; fields=['id','producto','producto_detalle','cantidad','subtotal']
 def get_subtotal(self,obj): return obj.producto.precio_con_descuento*obj.cantidad
class CarritoSerializer(serializers.ModelSerializer):
 items=ItemCarritoSerializer(many=True,read_only=True); cantidad_items=serializers.IntegerField(read_only=True); total_con_descuento=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True)
 class Meta: model=Carrito; fields=['id','usuario','items','cupon','cantidad_items','total_con_descuento','updated']; read_only_fields=['usuario','updated']
class OrdenSerializer(serializers.ModelSerializer):
 entrega_estimada=serializers.DateField(read_only=True)
 class Meta: model=Orden; fields=['id','usuario','items_snapshot','direccion_envio','metodo_pago','estado','subtotal','total','numero_seguimiento','fecha_creacion','entrega_estimada']; read_only_fields=['usuario','items_snapshot','estado','subtotal','total','numero_seguimiento','fecha_creacion']
class ResenaSerializer(serializers.ModelSerializer):
 usuario_nombre=serializers.CharField(source='usuario.username',read_only=True); es_compra_verificada=serializers.SerializerMethodField()
 class Meta: model=Resena; fields=['id','usuario','usuario_nombre','producto','calificacion','titulo','comentario','es_compra_verificada','fecha_creacion']; read_only_fields=['usuario','fecha_creacion']
 def get_es_compra_verificada(self,obj): return Orden.objects.filter(usuario=obj.usuario,estado__in=['pagada','enviada','entregada'],items_snapshot__contains=[{'producto_id':obj.producto_id}]).exists()
 def validate_calificacion(self,value):
  if not 1<=value<=5: raise serializers.ValidationError('La calificación debe estar entre 1 y 5.')
  return value
 def validate(self,data):
  req=self.context['request']; pid=data.get('producto',getattr(self.instance,'producto',None))
  if pid and not Orden.objects.filter(usuario=req.user,estado__in=['pagada','enviada','entregada'],items_snapshot__contains=[{'producto_id':pid.pk}]).exists(): raise serializers.ValidationError('Solo se puede reseñar un producto comprado.')
  return data
