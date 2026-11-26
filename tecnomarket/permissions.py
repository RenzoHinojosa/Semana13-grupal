from rest_framework import permissions
class EsVendedorPropietarioOAdmin(permissions.BasePermission):
 def has_permission(self,request,view): return request.user.is_authenticated
 def has_object_permission(self,request,view,obj): return request.user.is_staff or obj.vendedor.usuario_id==request.user.id
class PropietarioOAdmin(permissions.BasePermission):
 def has_permission(self,request,view): return request.user.is_authenticated
 def has_object_permission(self,request,view,obj):
  owner=getattr(obj,'usuario_id',None)
  if hasattr(obj,'carrito'): owner=obj.carrito.usuario_id
  return request.user.is_staff or owner==request.user.id
class PuedeVender(permissions.BasePermission):
 def has_permission(self,request,view): return request.user.is_authenticated and (request.user.is_staff or hasattr(request.user,'perfil_vendedor'))
