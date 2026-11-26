from django.urls import include,path
from rest_framework.routers import DefaultRouter
from . import views
router=DefaultRouter(); router.register('categorias',views.CategoriaViewSet); router.register('productos',views.ProductoViewSet); router.register('carrito',views.CarritoViewSet,basename='carrito'); router.register('ordenes',views.OrdenViewSet); router.register('resenas',views.ResenaViewSet)
urlpatterns=[path('',include(router.urls))]
