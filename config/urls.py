from django.contrib import admin
from django.urls import include,path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from drf_spectacular.views import SpectacularAPIView,SpectacularRedocView,SpectacularSwaggerView
from biblioteca.views import AutorViewSet,LibroViewSet,PrestamoViewSet,pagina_libros
from rest_framework.routers import DefaultRouter
from tecnomarket.views import CategoriaViewSet as MarketCategoriaViewSet,ProductoViewSet as MarketProductoViewSet,CarritoViewSet,OrdenViewSet,ResenaViewSet,pagina_productos
library=DefaultRouter(); library.register('autores',AutorViewSet); library.register('libros',LibroViewSet); library.register('prestamos',PrestamoViewSet)
market=DefaultRouter(); market.register('categorias',MarketCategoriaViewSet); market.register('productos',MarketProductoViewSet); market.register('carrito',CarritoViewSet,basename='carrito'); market.register('ordenes',OrdenViewSet); market.register('resenas',ResenaViewSet)
urlpatterns=[path('',TemplateView.as_view(template_name='home.html'),name='home'),path('catalogo/libros/',pagina_libros,name='catalogo-libros'),path('catalogo/productos/',pagina_productos,name='catalogo-productos'),path('admin/',admin.site.urls),path('api/biblioteca/',include(library.urls)),path('api/',include(market.urls)),path('api/schema/',SpectacularAPIView.as_view(),name='schema'),path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui'),path('api/redoc/',SpectacularRedocView.as_view(url_name='schema'),name='redoc'),path('api-auth/',include('rest_framework.urls')),path('api/token/',obtain_auth_token)]
