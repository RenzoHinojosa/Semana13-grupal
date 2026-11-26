from datetime import date
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions,viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from .models import Autor,Libro,Prestamo
from .pagination import PaginaBiblioteca
from .permissions import EsBibliotecarioOAdmin,PropietarioOAdmin
from .serializers import AutorSerializer,LibroSerializer,PrestamoSerializer
def pagina_libros(request):
 qs=Libro.objects.select_related('autor').all().order_by('titulo'); params=request.GET; search=params.get('search','').strip(); category=params.get('categoria',''); year=params.get('anio',''); available=params.get('disponible','')
 if search: qs=qs.filter(Q(titulo__icontains=search)|Q(isbn__icontains=search)|Q(autor__nombre__icontains=search))
 if category: qs=qs.filter(categoria=category)
 if year:
  try: qs=qs.filter(anio=int(year))
  except ValueError: year=''
 if available=='true': qs=qs.filter(stock__gt=0)
 elif available=='false': qs=qs.filter(stock=0)
 page_obj=Paginator(qs,20).get_page(request.GET.get('page')); query={k:v for k,v in params.items() if k!='page' and v}; querystring='&'.join(f'{k}={v}' for k,v in query.items())
 return render(request,'catalogo_libros.html',{'libros':page_obj.object_list,'page_obj':page_obj,'categorias':Libro.objects.order_by().values_list('categoria',flat=True).distinct(),'filters':{'search':search,'categoria':category,'anio':year,'disponible':available},'querystring':querystring})
class AutorViewSet(viewsets.ModelViewSet):
 queryset=Autor.objects.all(); serializer_class=AutorSerializer; permission_classes=[permissions.IsAuthenticatedOrReadOnly]
class LibroViewSet(viewsets.ModelViewSet):
 throttle_scope="burst"
 queryset=Libro.objects.select_related('autor').all(); serializer_class=LibroSerializer; pagination_class=PaginaBiblioteca; search_fields=['titulo','isbn','autor__nombre']; ordering_fields=['anio','titulo']; filterset_fields=['categoria','anio']; ordering='titulo'
 def get_queryset(self):
  qs=super().get_queryset(); disponible=self.request.query_params.get('disponible')
  if disponible is not None: qs=qs.filter(stock__gt=0) if disponible.lower()=='true' else qs.filter(stock=0)
  return qs
 def get_permissions(self):
  if self.action in ['create','update','partial_update']: return [EsBibliotecarioOAdmin()]
  if self.action=='destroy': return [permissions.IsAdminUser()]
  return [permissions.AllowAny()]
class PrestamoViewSet(viewsets.ModelViewSet):
 throttle_scope="checkout"
 queryset=Prestamo.objects.select_related('libro','usuario').all(); serializer_class=PrestamoSerializer; pagination_class=PaginaBiblioteca
 def get_permissions(self):
  if self.action in ['list']:
   return [permissions.IsAdminUser()]
  if self.action in ['create','update','partial_update','devolver']: return [EsBibliotecarioOAdmin()]
  if self.action=='destroy': return [permissions.IsAdminUser()]
  if self.action in ['retrieve']: return [permissions.IsAuthenticated(),PropietarioOAdmin()]
  return [permissions.IsAdminUser()]
 def get_queryset(self):
  qs=super().get_queryset()
  if self.request.user.is_staff: return qs
  if self.request.user.is_authenticated: return qs.filter(usuario=self.request.user)
  return qs.none()
 @transaction.atomic
 def perform_create(self,serializer):
  user=serializer.validated_data.get('usuario') or self.request.user
  libro=serializer.validated_data['libro']; libro=Libro.objects.select_for_update().get(pk=libro.pk)
  if libro.stock<1: raise ValidationError({'libro':'No hay ejemplares disponibles.'})
  if user.prestamos.filter(estado='activo').count()>=5: raise ValidationError('Límite de 5 préstamos activos.')
  libro.stock-=1; libro.save(update_fields=['stock']); serializer.save(usuario=user)
 @action(detail=True,methods=['post'])
 def devolver(self,request,pk=None):
  p=self.get_object()
  if p.estado=='devuelto': return Response(PrestamoSerializer(p,context={'request':request}).data)
  p.estado='devuelto'; p.libro.stock+=1; p.libro.save(update_fields=['stock']); p.save(update_fields=['estado']); return Response(PrestamoSerializer(p,context={'request':request}).data)
 @action(detail=False,methods=['get'])
 def vencidos(self,request):
  return Response(PrestamoSerializer(self.get_queryset().filter(fecha_devolucion__lt=date.today(),estado='activo'),many=True,context={'request':request}).data)
