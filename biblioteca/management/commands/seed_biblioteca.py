from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token
from biblioteca.models import Autor,Libro
class Command(BaseCommand):
 help='Carga datos de prueba del caso biblioteca.'
 @transaction.atomic
 def handle(self,*args,**options):
  User=get_user_model(); admin,_=User.objects.get_or_create(username='admin',defaults={'is_staff':True,'is_superuser':True,'email':'admin@biblioteca.local'}); admin.is_staff=True; admin.is_superuser=True; admin.set_password('admin12345'); admin.save(); Token.objects.get_or_create(user=admin)
  group,_=Group.objects.get_or_create(name='Bibliotecario')
  librarian,_=User.objects.get_or_create(username='bibliotecario',defaults={'email':'bibliotecario@biblioteca.local'}); librarian.set_password('biblio12345'); librarian.save(); librarian.groups.add(group); Token.objects.get_or_create(user=librarian)
  for i in range(1,11):
   u,_=User.objects.get_or_create(username=f'estudiante{i:02d}',defaults={'email':f'estudiante{i:02d}@biblioteca.local'}); u.set_password('estudiante123'); u.save(); Token.objects.get_or_create(user=u)
  authors=[]
  for name,nationality in [('Gabriel García Márquez','Colombiana'),('César Vallejo','Peruana'),('Mario Vargas Llosa','Peruana'),('Isabel Allende','Chilena'),('Jorge Luis Borges','Argentina')]: authors.append(Autor.objects.get_or_create(nombre=name,defaults={'nacionalidad':nationality})[0])
  titles=['Cien años de soledad','El principito','Tradiciones peruanas','La ciudad y los perros','Los ríos profundos','Ficciones','Conversación en La Catedral','Paco Yunque','Rayuela','La casa de los espíritus']
  for i in range(50): Libro.objects.get_or_create(isbn=f'978-612-{i+1:06d}',defaults={'titulo':titles[i%len(titles)]+(f' {i//10+1}' if i>=10 else ''),'autor':authors[i%len(authors)],'editorial':'Editorial Académica','anio':2000+i%25,'categoria':['Literatura','Ingeniería','Ciencias'][i%3],'stock':2+i%5,'ubicacion':f'Estante {i%8+1}/Piso {i%3+1}'})
  self.stdout.write(self.style.SUCCESS('Caso biblioteca cargado: admin/admin12345, bibliotecario/biblio12345, estudiante01-10/estudiante123; 50 libros.'))
