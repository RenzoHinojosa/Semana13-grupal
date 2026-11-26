from django.contrib import admin
from .models import Autor,Libro,Prestamo
@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin): list_display=('nombre','nacionalidad'); search_fields=('nombre',)
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin): list_display=('titulo','isbn','autor','anio','stock'); list_filter=('categoria','anio'); search_fields=('titulo','isbn','autor__nombre')
@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin): list_display=('usuario','libro','fecha_prestamo','fecha_devolucion','estado'); list_filter=('estado',)
