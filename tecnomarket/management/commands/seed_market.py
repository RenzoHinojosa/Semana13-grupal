from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token
from tecnomarket.models import Categoria,Producto,Vendedor
import random
from decimal import Decimal
ITEMS=[('Laptop Gamer RTX 4060',2800),('Laptop Ultrabook i7',3200),('Smartphone Pro 256GB',2400),('Smartphone 5G 128GB',1100),('Monitor 27 pulgadas 144Hz',900),('Teclado mecánico RGB',220),('Mouse inalámbrico gaming',130),('Audífonos Bluetooth ANC',350),('SSD NVMe 1TB',310),('Tablet 11 pulgadas',1250),('Tarjeta gráfica RTX 4070',2800),('Router WiFi 6',280),('Webcam Full HD',180),('Parlante portátil',160),('Memoria RAM DDR5 16GB',240)]
class Command(BaseCommand):
 help='Carga datos realistas del marketplace TecnoMarket.'
 @transaction.atomic
 def handle(self,*args,**options):
  User=get_user_model(); admin,_=User.objects.get_or_create(username='admin',defaults={'email':'admin@tecnomarket.local','is_staff':True,'is_superuser':True}); admin.is_staff=True; admin.is_superuser=True; admin.set_password('admin12345'); admin.save(); Token.objects.get_or_create(user=admin)
  for i in range(1,21):
   u,_=User.objects.get_or_create(username=f'cliente{i:02d}',defaults={'email':f'cliente{i:02d}@tecnomarket.local'}); u.set_password('cliente123'); u.save(); Token.objects.get_or_create(user=u)
  for i in range(1,6):
   u,_=User.objects.get_or_create(username=f'vendedor{i:02d}',defaults={'email':f'vendedor{i:02d}@tecnomarket.local'}); u.set_password('vendedor123'); u.save(); Token.objects.get_or_create(user=u); Vendedor.objects.get_or_create(usuario=u,defaults={'nombre_tienda':f'Tienda Tecno {i}','slug':f'tienda-tecno-{i}','verificado':True})
  cats=[Categoria.objects.get_or_create(nombre=n,defaults={'descripcion':f'Productos de {n}'})[0] for n in ['Laptops','Smartphones','Componentes','Accesorios','Redes y tablets']]; vendors=list(Vendedor.objects.all()); brands=['NovaTech','PeruDigital','AndesGadget','ByteMarket','InkaTech']; random.seed(13)
  for i in range(100):
   name,price=ITEMS[i%len(ITEMS)]; producto,_=Producto.objects.get_or_create(sku=f'TM-{i+1:05d}',defaults={'nombre':name+(f' Gen {i//len(ITEMS)+1}' if i>=len(ITEMS) else ''),'descripcion':f'{name}: producto tecnológico para el catálogo TecnoMarket Perú.','marca':brands[i%len(brands)],'categoria':cats[i%len(cats)],'vendedor':vendors[i%len(vendors)],'precio':Decimal(price+i%70),'descuento':Decimal(random.choice([0,0,5,10,15])),'stock':random.randint(0,40),'imagenes':[],'especificaciones':{'garantia':'12 meses','origen':'Perú','sku_demo':i+1}});
   if producto.imagenes: producto.imagenes=[]; producto.save(update_fields=['imagenes'])
  self.stdout.write(self.style.SUCCESS('TecnoMarket cargado: admin/admin12345, cliente01-20/cliente123, vendedor01-05/vendedor123; 100 productos.'))
