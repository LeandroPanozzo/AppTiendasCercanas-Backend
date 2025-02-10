from django.db import models
from django.contrib.auth.models import User
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from django.core.exceptions import ValidationError
from django.db.models import TextChoices
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import PermissionDenied, ValidationError


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tiene_comercio = models.BooleanField(default=False)
    direccion_calle = models.CharField(max_length=100, blank=True)
    direccion_numero = models.CharField(max_length=10, blank=True)
    ciudad = models.CharField(max_length=50, blank=True)
    coordenada_latitud = models.FloatField(null=True, blank=True)
    coordenada_longitud = models.FloatField(null=True, blank=True)
    rango_busqueda_km = models.FloatField(default=10)
    provincia = models.CharField(max_length=50, default="Buenos Aires")

    def tiendas_cercanas(self):
        """Encuentra tiendas dentro del rango de búsqueda del usuario."""
        if self.coordenada_latitud is None or self.coordenada_longitud is None:
            raise ValidationError("El perfil no tiene coordenadas válidas.")

        tiendas = Tienda.objects.all()
        tiendas_cercanas = []
        for tienda in tiendas:
            if tienda.coordenada_latitud and tienda.coordenada_longitud:
                distancia = geodesic(
                    (self.coordenada_latitud, self.coordenada_longitud),
                    (tienda.coordenada_latitud, tienda.coordenada_longitud)
                ).kilometers
                if distancia <= self.rango_busqueda_km:
                    tiendas_cercanas.append((tienda, distancia))
        return sorted(tiendas_cercanas, key=lambda x: x[1])

    def __str__(self):
        return self.user.username
    
    def obtener_coordenadas(self):
        return {
            'latitud': self.coordenada_latitud,
            'longitud': self.coordenada_longitud
        }
class DiasAtencionChoices(TextChoices):
    LUNES_A_VIERNES = "lunes_a_viernes", "Lunes a Viernes"
    LUNES_A_SABADO = "lunes_a_sabado", "Lunes a Sabado"
    TODOS_LOS_DIAS = "todos_los_dias", "Todos los dias"


class CategoriaTiendaChoices(TextChoices):
    RESTAURANTE = "restaurante", "Restaurante"
    SUPERMERCADO = "supermercado", "Supermercado"
    ROPA = "ropa", "Ropa"
    TECNOLOGIA = "tecnologia", "Tecnologia"
    BELLEZA = "belleza", "Belleza"
    DEPORTES = "deportes", "Deportes"
    VETERINARIA = "veterinaria", "Veterinaria"
    SALUD = "salud", "Salud"
    AUTOPARTES = "autopartes", "Autopartes"
    CONSTRUCCION_Y_FERRETERIA = "construccion_y_ferreteria", "Construccion y Ferreteria"
    POLIRUBRO = "polirrubro", "Polirrubro"
    OTROS = "otros", "Otros"



class Tienda(models.Model):
    efectivo = models.BooleanField(default=False)
    debito = models.BooleanField(default=False)
    credito = models.BooleanField(default=False)
    transferencia_bancaria = models.BooleanField(default=False)
    pago_movil = models.BooleanField(default=False)
    qr = models.BooleanField(default=False)
    monedero_electronico = models.BooleanField(default=False)
    criptomoneda = models.BooleanField(default=False)
    pasarela_en_linea = models.BooleanField(default=False)
    cheque = models.BooleanField(default=False)
    pagos_a_plazos = models.BooleanField(default=False)
    vales = models.BooleanField(default=False)
    contra_entrega = models.BooleanField(default=False)
    debito_directo = models.BooleanField(default=False)
    creditos_internos = models.BooleanField(default=False)
    url_logo = models.URLField(blank=True, null=True, help_text="URL del logo de la tienda en Imgur")
    propietario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="tiendas")
    nombre = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50, default="Buenos Aires")
    ciudad = models.CharField(max_length=50)
    coordenada_latitud = models.FloatField(null=True, blank=True)
    coordenada_longitud = models.FloatField(null=True, blank=True)
    descripcion = models.TextField()
    direccion_calle = models.CharField(max_length=100)
    direccion_numero = models.CharField(max_length=10)
    permite_reservas = models.BooleanField(default=True, help_text="Habilita/deshabilita las reservas para toda la tienda")
    categoria = models.CharField(
        max_length=50, choices=CategoriaTiendaChoices.choices, default=CategoriaTiendaChoices.OTROS
    )
    dias_atencion = models.CharField(
        max_length=50, choices=DiasAtencionChoices.choices, default=DiasAtencionChoices.LUNES_A_VIERNES
    )
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    # Nuevo campo para WhatsApp
    whatsapp = models.CharField(max_length=20, blank=True, null=True, help_text="Número de WhatsApp incluyendo código de país")
    
    def __str__(self):
        return self.nombre

    def obtener_coordenadas(self):
        return {
            'latitud': self.coordenada_latitud,
            'longitud': self.coordenada_longitud
        }
    
    # Nuevo método para obtener el link de WhatsApp
    def obtener_link_whatsapp(self):
        if self.whatsapp:
            # Elimina espacios y caracteres especiales
            numero_limpio = ''.join(filter(str.isdigit, self.whatsapp))
            return f"https://wa.me/{numero_limpio}"
        return None

class Producto(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name="productos")
    categoria = models.CharField(max_length=50)
     # Add the new logo URL field
    nombre = models.CharField(max_length=100)
    url_imagen = models.URLField()
    estado_publicacion = models.CharField(max_length=50)
    disponibilidad = models.BooleanField(default=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cantidad_disponible = models.IntegerField(null=True, blank=True)
    es_servicio = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    permite_reservas = models.BooleanField(
        default=True,
        help_text="Permite reservar este producto específico"
    )
    # Nuevos campos para promociones
    UNIDADES_CHOICES = [
        (1, "primera"),
        (2, "segunda"),
        (3, "tercera"),
        (4, "cuarta"),
        (5, "quinta"),
        (6, "sexta"),
        (7, "séptima"),
        (8, "octava"),
        (9, "novena"),
        (10, "décima"),
    ]
    
    promocion_nx = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        help_text="Formato: 'NxM' (ejemplo: '2x1', '3x2')"
    )
    
    promocion_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Porcentaje de descuento para la unidad específica"
    )
    
    promocion_unidad = models.IntegerField(
        choices=UNIDADES_CHOICES,
        null=True,
        blank=True,
        help_text="Unidad a la que se aplica el descuento porcentual"
    )

    def clean(self):
        # Validación para el formato de promocion_nx
        if self.promocion_nx:
            import re
            if not re.match(r'^\d+x\d+$', self.promocion_nx):
                raise ValidationError({
                    'promocion_nx': 'El formato debe ser "NxM" (ejemplo: "2x1", "3x2")'
                })
            
        # Validación para promoción porcentual
        if (self.promocion_porcentaje is not None and self.promocion_unidad is None) or \
           (self.promocion_porcentaje is None and self.promocion_unidad is not None):
            raise ValidationError(
                'Debe especificar tanto el porcentaje como la unidad para la promoción porcentual'
            )

        if self.promocion_porcentaje is not None and \
           (self.promocion_porcentaje < 0 or self.promocion_porcentaje > 100):
            raise ValidationError({
                'promocion_porcentaje': 'El porcentaje debe estar entre 0 y 100'
            })
    def is_reservable(self):
        return (
            self.permite_reservas and 
            self.tienda.permite_reservas and 
            self.disponibilidad and 
            not self.es_servicio and
            (self.cantidad_disponible is None or self.cantidad_disponible > 0)
        )

    def save(self, *args, **kwargs):
        if not self.id and not self.precio_original:
            self.precio_original = self.precio
        elif self.precio < self.precio_original:
            self.porcentaje_descuento = ((self.precio_original - self.precio) / self.precio_original) * 100
        else:
            self.porcentaje_descuento = 0
        
        if self.es_servicio:
            self.cantidad_disponible = None

        super().save(*args, **kwargs)

class EstadoReserva(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    RETIRADO = 'retirado', 'Retirado'
    CANCELADA = 'cancelada', 'Cancelada'


class Reserva(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reservas")
    confirmacion_retirada = models.BooleanField(default=False, help_text="Confirmación por parte del propietario de la tienda")
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name="reservas")
    productos = models.ManyToManyField('Producto', through='ReservaProducto', related_name="reservas_producto")
    fecha_reserva = models.DateField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE
    )

    def __str__(self):
        return f"Reserva de {self.usuario.user.username} en {self.tienda.nombre}"

    def save(self, *args, **kwargs):

        # Si es una nueva reserva (no tiene ID)
        if not self.id:
            # Establece la fecha límite a 7 días después de la fecha de reserva
            self.fecha_limite = timezone.now() + timedelta(days=7)

        if self.id:
            for producto in self.productos.all():
                if not producto.disponibilidad or producto.es_servicio:
                    raise ValidationError(f"El producto '{producto.nombre}' no está disponible para reserva.")
        
        super().save(*args, **kwargs)

    def cancel(self, user, cancellation_type="cancelada"):
        if self.estado in [EstadoReserva.CANCELADA, EstadoReserva.VENCIDA]:
            raise ValidationError("La reserva ya está cancelada o vencida.")

        if user != self.tienda.propietario and user != self.usuario:
            raise PermissionDenied("Solo el propietario de la tienda o el usuario que reservó pueden cancelar esta reserva.")

        self.estado = cancellation_type
        self.save()

        for reserva_producto in self.reserva_productos.all():
            producto = reserva_producto.producto
            if producto.cantidad_disponible is not None:
                producto.cantidad_disponible += reserva_producto.cantidad
                producto.save()

    def mark_as_collected(self):
        if self.estado == EstadoReserva.PENDIENTE:
            self.estado = EstadoReserva.RETIRADA
            self.save()
            return True
        return False

    def check_expiration(self):
        if (self.estado == EstadoReserva.PENDIENTE and 
            timezone.now() > self.fecha_limite):
            self.cancel(cancellation_type=EstadoReserva.VENCIDA)
            return True
        if (self.estado == EstadoReserva.RETIRADO and 
            timezone.now() > (self.fecha_limite + timedelta(days=30))):
            self.delete()
            return True
        
        return False

    def marcar_como_retirada(self, user):
        if user != self.usuario:
            raise PermissionDenied("Solo el usuario que realizó la reserva puede marcarla como retirada.")
        
        if self.estado != EstadoReserva.PENDIENTE:
            raise ValidationError("Solo se pueden marcar como retiradas las reservas pendientes.")

        self.estado = EstadoReserva.RETIRADA
        self.save()

    def confirmar_retirada(self, user):
        if user != self.tienda.propietario:
            raise PermissionDenied("Solo el propietario de la tienda puede confirmar la retirada.")
        
        if self.estado != EstadoReserva.RETIRADA:
            raise ValidationError("Solo se pueden confirmar retiradas las reservas marcadas como retiradas.")

        self.confirmacion_retirada = True
        self.save()

    def rechazar_retirada(self, user):
        if user != self.tienda.propietario:
            raise PermissionDenied("Solo el propietario de la tienda puede rechazar la retirada.")
        
        if self.estado != EstadoReserva.RETIRADA:
            raise ValidationError("Solo se pueden rechazar retiradas las reservas marcadas como retiradas.")

        self.estado = EstadoReserva.PENDIENTE
        self.save()

class ReservaProducto(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="reserva_productos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="producto_reservas")
    cantidad = models.PositiveIntegerField()

    def clean(self):
        if not self.producto.disponibilidad:
            raise ValidationError(f"El producto '{self.producto.nombre}' no está disponible para reserva.")
        
        if self.producto.es_servicio:
            raise ValidationError(f"No se pueden reservar servicios.")
        
        if (self.producto.cantidad_disponible is not None and 
            self.cantidad > self.producto.cantidad_disponible):
            raise ValidationError(
                f"No hay suficiente cantidad disponible para el producto '{self.producto.nombre}'."
            )

    def save(self, *args, **kwargs):
        self.clean()
        
        if self.producto.cantidad_disponible is not None:
            self.producto.cantidad_disponible -= self.cantidad
            self.producto.save()

        super().save(*args, **kwargs)
from django.db.models.signals import post_save
from django.dispatch import receiver
@receiver(post_save, sender=Reserva)
def limpiar_reservas_antiguas(sender, instance, **kwargs):
    fecha_limite = timezone.now().date() - timedelta(days=7)
    
    # Elimina las reservas antiguas que estén en estado PENDIENTE o RETIRADO
    Reserva.objects.filter(
        fecha_reserva__lt=fecha_limite,
        estado__in=[EstadoReserva.PENDIENTE, EstadoReserva.RETIRADO]
    ).delete()

class Notificacion(models.Model):
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50)
    
    class Meta:
        ordering = ['-fecha_creacion']

@receiver(post_save, sender=Notificacion)
def limpiar_notificaciones_antiguas(sender, instance, **kwargs):
    # Eliminar notificaciones leídas
    Notificacion.objects.filter(
        leida=True
    ).delete()
    
    # Eliminar notificaciones no leídas más antiguas de 30 días
    fecha_limite = timezone.now() - timedelta(days=30)
    Notificacion.objects.filter(
        leida=False,
        fecha_creacion__lt=fecha_limite
    ).delete()
def limpiar_notificaciones():
    # Eliminar notificaciones leídas
    Notificacion.objects.filter(
        leida=True
    ).delete()
    
    # Eliminar notificaciones no leídas más antiguas de 30 días
    fecha_limite = timezone.now() - timedelta(days=30)
    Notificacion.objects.filter(
        leida=False,
        fecha_creacion__lt=fecha_limite
    ).delete()
        
class Contiene(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="contenidos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="reservas")
    cantidad = models.IntegerField()

    class Meta:
        unique_together = ("reserva", "producto")

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en reserva {self.reserva.id}"


class DetalleReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_reservada = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.id_detalle_reserva} - Reserva {self.reserva.id}"

