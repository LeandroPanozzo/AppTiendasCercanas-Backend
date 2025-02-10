from django.contrib import admin
from .models import Profile
from .models import Tienda
from .models import Producto
from .models import Reserva
from .models import Contiene
from .models import DetalleReserva


admin.site.register(Profile)
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(Reserva)
admin.site.register(Contiene)
admin.site.register(DetalleReserva)

# Register your models here.
