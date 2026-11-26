from rest_framework import permissions
class EsBibliotecarioOAdmin(permissions.BasePermission):
 def has_permission(self,request,view): return request.user.is_authenticated and (request.user.is_staff or request.user.groups.filter(name='Bibliotecario').exists())
class PropietarioOAdmin(permissions.BasePermission):
 def has_object_permission(self,request,view,obj): return request.user.is_staff or obj.usuario_id==request.user.id
