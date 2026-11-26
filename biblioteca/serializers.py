from rest_framework import serializers
from .models import Autor,Libro,Prestamo
class AutorSerializer(serializers.ModelSerializer):
 class Meta: model=Autor; fields=['id','nombre','nacionalidad','biografia']
class LibroSerializer(serializers.HyperlinkedModelSerializer):
 autor_detalle=AutorSerializer(source='autor',read_only=True); disponible=serializers.ReadOnlyField()
 class Meta: model=Libro; fields=['url','id','isbn','titulo','autor','autor_detalle','editorial','anio','categoria','stock','ubicacion','disponible']
class PrestamoSerializer(serializers.ModelSerializer):
 dias_restantes=serializers.SerializerMethodField(); multa_estimada=serializers.SerializerMethodField()
 class Meta: model=Prestamo; fields=['id','usuario','libro','fecha_prestamo','fecha_devolucion','estado','dias_restantes','multa_estimada']; read_only_fields=['fecha_prestamo','estado']
 def get_dias_restantes(self,obj):
  from datetime import date
  return (obj.fecha_devolucion-date.today()).days
 def get_multa_estimada(self,obj): return max(0,-self.get_dias_restantes(obj))*2.0 if obj.estado=='vencido' else 0.0
 def validate(self,data):
  request=self.context.get('request'); user=data.get('usuario') or getattr(self.instance,'usuario',None) or getattr(request,'user',None)
  libro=data.get('libro') or getattr(self.instance,'libro',None)
  if user and user.is_authenticated and user.prestamos.filter(estado='activo').exclude(pk=getattr(self.instance,'pk',None)).count()>=5: raise serializers.ValidationError('El usuario ya tiene 5 préstamos activos.')
  if libro and not libro.disponible: raise serializers.ValidationError({'libro':'El libro no tiene stock disponible.'})
  return data
