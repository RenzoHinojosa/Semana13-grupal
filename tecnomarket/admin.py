from django.contrib import admin
from .models import Categoria,Carrito,ItemCarrito,Orden,Producto,Resena,Vendedor
admin.site.register([Categoria,Vendedor,Carrito,ItemCarrito,Orden,Resena])
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin): list_display=('sku','nombre','marca','categoria','precio','stock','vendedor'); search_fields=('sku','nombre','marca'); list_filter=('categoria','marca')
