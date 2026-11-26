from decimal import Decimal
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db import transaction
from django.db.models import Avg, Q
from rest_framework import filters,permissions,viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Categoria,Carrito,ItemCarrito,Orden,Producto,Resena,Vendedor
from .pagination import PaginaProductos,PaginaCatalogoCompacta
from .permissions import EsVendedorPropietarioOAdmin,PropietarioOAdmin
from .serializers import CategoriaSerializer,CarritoSerializer,OrdenSerializer,ProductoSerializer,ResenaSerializer
def pagina_productos(request):
 qs=Producto.objects.select_related('categoria','vendedor').annotate(rating_sort=Avg('resenas__calificacion')).order_by('nombre')
 params=request.GET; search=params.get('search','').strip(); category=params.get('categoria',''); brand=params.get('marca','').strip(); pmin=params.get('precio_min',''); pmax=params.get('precio_max',''); available=params.get('disponible','')
 if search: qs=qs.filter(Q(nombre__icontains=search)|Q(marca__icontains=search)|Q(descripcion__icontains=search)|Q(sku__icontains=search))
 if category: qs=qs.filter(categoria_id=category)
 if brand: qs=qs.filter(marca__icontains=brand)
 if pmin:
  try: qs=qs.filter(precio__gte=Decimal(pmin))
  except Exception: pmin=''
 if pmax:
  try: qs=qs.filter(precio__lte=Decimal(pmax))
  except Exception: pmax=''
 if available=='true': qs=qs.filter(stock__gt=0)
 elif available=='false': qs=qs.filter(stock=0)
 page_obj=Paginator(qs,24).get_page(request.GET.get('page'))
 query={k:v for k,v in params.items() if k!='page' and v}; querystring='&'.join(f'{k}={v}' for k,v in query.items())
 return render(request,'catalogo_productos.html',{'productos':page_obj.object_list,'page_obj':page_obj,'categorias':Categoria.objects.all(),'filters':{'search':search,'categoria':category,'marca':brand,'precio_min':pmin,'precio_max':pmax,'disponible':available},'querystring':querystring})
class CategoriaViewSet(viewsets.ReadOnlyModelViewSet): queryset=Categoria.objects.all(); serializer_class=CategoriaSerializer; pagination_class=PaginaCatalogoCompacta
class ProductoViewSet(viewsets.ModelViewSet):
 throttle_scope="burst"
 queryset=Producto.objects.select_related('categoria','vendedor').all(); serializer_class=ProductoSerializer; pagination_class=PaginaProductos; search_fields=['nombre','descripcion','marca','sku','categoria__nombre']; ordering_fields=['precio','rating_sort','created','nombre']; order_by='nombre'; filterset_fields=['categoria','marca']
 def get_queryset(self):
  qs=super().get_queryset().annotate(rating_sort=Avg('resenas__calificacion')).order_by('nombre'); p=self.request.query_params
  if p.get('precio_min'): qs=qs.filter(precio__gte=p['precio_min'])
  if p.get('precio_max'): qs=qs.filter(precio__lte=p['precio_max'])
  if p.get('disponible','').lower()=='true': qs=qs.filter(stock__gt=0)
  if p.get('disponible','').lower()=='false': qs=qs.filter(stock=0)
  return qs
 def get_permissions(self):
  if self.action=='create': return [permissions.IsAuthenticated()]
  if self.action in ['update','partial_update']: return [EsVendedorPropietarioOAdmin()]
  if self.action=='destroy': return [permissions.IsAdminUser()]
  return [permissions.AllowAny()]
 def perform_create(self,serializer):
  vendedor=Vendedor.objects.filter(usuario=self.request.user).first()
  if not vendedor and self.request.user.is_staff: vendedor=Vendedor.objects.first()
  if not vendedor: raise ValidationError('Se requiere un perfil de vendedor aprobado.')
  serializer.save(vendedor=vendedor)
 @action(detail=True,methods=['get'])
 def resenas(self,request,pk=None): return Response(ResenaSerializer(self.get_object().resenas.all(),many=True,context={'request':request}).data)
class CarritoViewSet(viewsets.ViewSet):
 throttle_scope="checkout"
 permission_classes=[permissions.IsAuthenticated,PropietarioOAdmin]
 def retrieve(self,request):
  carrito,_=Carrito.objects.get_or_create(usuario=request.user); return Response(CarritoSerializer(carrito,context={'request':request}).data)
 def list(self,request): return self.retrieve(request)
 def _cart(self,request): return Carrito.objects.get_or_create(usuario=request.user)[0]
 @action(detail=False,methods=['post'])
 def agregar(self,request):
  cart=self._cart(request); product=Producto.objects.get(pk=request.data.get('producto')); qty=int(request.data.get('cantidad',1))
  if qty<1 or qty>product.stock: raise ValidationError('Cantidad inválida o superior al stock disponible.')
  item,_=ItemCarrito.objects.get_or_create(carrito=cart,producto=product,defaults={'cantidad':0})
  if item.cantidad+qty>product.stock: raise ValidationError('La cantidad supera el stock disponible.')
  item.cantidad+=qty; item.save(); return Response(CarritoSerializer(cart,context={'request':request}).data)
 @action(detail=False,methods=['post'])
 def actualizar(self,request):
  cart=self._cart(request); item=ItemCarrito.objects.get(carrito=cart,producto_id=request.data.get('producto')); qty=int(request.data.get('cantidad',1))
  if qty<1 or qty>item.producto.stock: raise ValidationError('Cantidad inválida o superior al stock disponible.')
  item.cantidad=qty; item.save(); return Response(CarritoSerializer(cart,context={'request':request}).data)
 @action(detail=False,methods=['post'])
 def eliminar(self,request):
  ItemCarrito.objects.filter(carrito=self._cart(request),producto_id=request.data.get('producto')).delete(); return Response(CarritoSerializer(self._cart(request),context={'request':request}).data)
 @action(detail=False,methods=['post'])
 def vaciar(self,request):
  cart=self._cart(request); cart.items.all().delete(); cart.cupon=''; cart.save(); return Response(CarritoSerializer(cart,context={'request':request}).data)
 @action(detail=False,methods=['post'])
 def checkout(self,request):
  self.throttle_scope="checkout"
  cart=self._cart(request)
  if not cart.items.exists(): raise ValidationError('El carrito está vacío.')
  with transaction.atomic():
   snapshot=[]; subtotal=Decimal('0')
   for item in cart.items.select_related('producto').select_for_update():
    if item.cantidad>item.producto.stock: raise ValidationError(f'Stock insuficiente para {item.producto.nombre}.')
    price=item.producto.precio_con_descuento; subtotal+=price*item.cantidad; snapshot.append({'producto_id':item.producto_id,'nombre':item.producto.nombre,'sku':item.producto.sku,'cantidad':item.cantidad,'precio_unitario':str(price)}); item.producto.stock-=item.cantidad; item.producto.save(update_fields=['stock'])
   total=cart.total_con_descuento; order=Orden.objects.create(usuario=request.user,items_snapshot=snapshot,direccion_envio=request.data.get('direccion_envio',{}),metodo_pago=request.data.get('metodo_pago','contra_entrega'),subtotal=subtotal,total=total); cart.items.all().delete(); cart.cupon=''; cart.save()
  return Response(OrdenSerializer(order,context={'request':request}).data,status=201)
class OrdenViewSet(viewsets.ModelViewSet):
 serializer_class=OrdenSerializer; queryset=Orden.objects.all(); permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):
  qs=super().get_queryset()
  return qs if self.request.user.is_staff else qs.filter(usuario=self.request.user)
 def get_permissions(self): return [permissions.IsAdminUser()] if self.action in ['update','partial_update','destroy'] else [permissions.IsAuthenticated()]
 @action(detail=False,methods=['get'])
 def mis_ordenes(self,request): return Response(OrdenSerializer(self.get_queryset().filter(usuario=request.user),many=True,context={'request':request}).data)
 @action(detail=True,methods=['post'])
 def cancelar(self,request,pk=None):
  order=self.get_object()
  if order.estado!='pendiente': raise ValidationError('Solo se pueden cancelar órdenes pendientes.')
  order.estado='cancelada'; order.save(update_fields=['estado']); return Response(OrdenSerializer(order,context={'request':request}).data)
class ResenaViewSet(viewsets.ModelViewSet):
 queryset=Resena.objects.select_related('usuario','producto').all(); serializer_class=ResenaSerializer; filterset_fields=['producto','calificacion']
 def get_permissions(self): return [permissions.AllowAny()] if self.action in ['list','retrieve'] else [permissions.IsAuthenticated(),PropietarioOAdmin()]
 def perform_create(self,serializer): serializer.save(usuario=self.request.user)
