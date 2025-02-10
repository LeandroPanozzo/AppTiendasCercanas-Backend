from djangoApiNegocio import settings
from rest_framework import viewsets, status
from .models import Profile, Tienda,  Producto, Reserva, Contiene, DetalleReserva
from .serializer import (
    ProfileSerializer, TiendaSerializer, ProductoSerializer,
    ReservaSerializer,NotificacionSerializer
)
from django.contrib.auth.models import User
from django.db import transaction
from .serializer import UserSerializer
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
import logging
import requests
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Profile
# En views.py cambiar:
from .serializer import ProfileSerializer# Vista para el modelo User
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token_serializer = TokenObtainPairSerializer(data={
                'username': request.data['username'],
                'password': request.data['password']
            })
            token_serializer.is_valid(raise_exception=True)
            return Response({
                'user': serializer.data,
                'tokens': token_serializer.validated_data
            }, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # Agregar esta línea para depuración
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"detail": "No tienes permiso para editar este perfil."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        profile = request.user.profile
        if request.method == 'PATCH':
            print("Received data:", request.data)  # Add this debug line
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            print("Validated data:", serializer.validated_data)  # Add this debug line
            serializer.save()
            return Response(serializer.data)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def tiendas_cercanas(self, request):
        try:
            tiendas = request.user.profile.tiendas_cercanas()
            return Response([{
                'tienda': TiendaSerializer(tienda).data,
                'distancia': round(distancia, 2)
            } for tienda, distancia in tiendas])
        except ValidationError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


# Configurar el logger
logger = logging.getLogger(__name__)

class TiendaViewSet(viewsets.ModelViewSet):
    queryset = Tienda.objects.all()
    serializer_class = TiendaSerializer
    IMGUR_CLIENT_ID = "b81c33853aa90f7"

    def upload_to_imgur(self, image):
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {self.IMGUR_CLIENT_ID}"}
        try:
            response = requests.post(
                url,
                headers=headers,
                files={"image": image},
            )
            response_data = response.json()
            if response.status_code == 200 and response_data.get("success"):
                return response_data["data"]["link"]
            else:
                raise ValidationError("Error al subir el logo a Imgur.")
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error al conectar con Imgur: {str(e)}")

    def get_serializer_context(self):
        return {'request': self.request}

    def partial_update(self, request, *args, **kwargs):
        tienda = self.get_object()
        logger.info(f"Actualizando tienda: {tienda.nombre} (ID: {tienda.id})")

        payment_methods = [
            'efectivo', 'debito', 'credito', 'transferencia_bancaria', 
            'pago_movil', 'qr', 'monedero_electronico', 'criptomoneda', 
            'pasarela_en_linea', 'cheque', 'pagos_a_plazos', 'vales', 
            'contra_entrega', 'debito_directo', 'creditos_internos'
        ]

        # Log which payment methods are being updated
        updated_methods = [
            method for method in payment_methods 
            if method in request.data
        ]
        
        if updated_methods:
            logger.info(f"Métodos de pago actualizados: {updated_methods}")

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        tienda = self.get_object()
        if request.user.profile != tienda.propietario:
            return Response({'error': 'No autorizado'}, status=403)
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(f"Datos completos de la tienda: {serializer.data}")
        return Response(serializer.data)

    def perform_create(self, serializer):
        logo = self.request.FILES.get("logo")
        if logo:
            imgur_url = self.upload_to_imgur(logo)
            serializer.save(url_logo=imgur_url)
        else:
            serializer.save()

    def perform_update(self, serializer):
        logo = self.request.FILES.get("logo")
        if logo:
            imgur_url = self.upload_to_imgur(logo)
            serializer.save(url_logo=imgur_url)
        else:
            serializer.save()
    def get_queryset(self):
        queryset = super().get_queryset()
        categoria = self.request.query_params.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        # Add payment method filtering
        payment_methods = [
            'efectivo', 'debito', 'credito', 'transferencia_bancaria', 
            'pago_movil', 'qr', 'monedero_electronico', 'criptomoneda', 
            'pasarela_en_linea', 'cheque', 'pagos_a_plazos', 'vales', 
            'contra_entrega', 'debito_directo', 'creditos_internos'
        ]

        for method in payment_methods:
            if self.request.query_params.get(method) == 'true':
                queryset = queryset.filter(**{method: True})
        
        return queryset
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
# Vista para el modelo Producto
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()  # Añade esta línea
    serializer_class = ProductoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tienda']
    ordering_fields = ['fecha_creacion']
    def get_queryset(self):
        queryset = Producto.objects.all()
        tienda_id = self.request.query_params.get('tienda', None)
        ciudad = self.request.query_params.get('ciudad', None)
        
        if tienda_id is not None:
            queryset = queryset.filter(tienda_id=tienda_id)
        if ciudad is not None:
            queryset = queryset.filter(tienda__ciudad=ciudad)
        
        # Get ordering parameter
        ordering = self.request.query_params.get('ordering', '-fecha_creacion')
        return queryset.order_by(ordering)

    IMGUR_CLIENT_ID = "b81c33853aa90f7"

    def upload_to_imgur(self, image):
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {self.IMGUR_CLIENT_ID}"}
        try:
            response = requests.post(
                url,
                headers=headers,
                files={"image": image},
            )
            response_data = response.json()
            if response.status_code == 200 and response_data.get("success"):
                return response_data["data"]["link"]
            else:
                raise ValidationError("Error al subir la imagen a Imgur.")
        except requests.exceptions.RequestException as e:
            raise ValidationError(f"Error al conectar con Imgur: {str(e)}")

    def perform_create(self, serializer):
        imagen = self.request.FILES.get("imagen")
        if imagen:
            imgur_url = self.upload_to_imgur(imagen)
            serializer.save(url_imagen=imgur_url)
        else:
            serializer.save()

    def perform_update(self, serializer):
        imagen = self.request.FILES.get("imagen")
        if imagen:
            imgur_url = self.upload_to_imgur(imagen)
            serializer.save(url_imagen=imgur_url)
        else:
            serializer.save()


# Vista para el modelo Reserva

from .models import Reserva, EstadoReserva

# En views.py
from django.db.models.signals import post_save
from django.dispatch import receiver

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    
    def perform_create(self, serializer):
        # Guardamos la reserva
        reserva = serializer.save(
            usuario=self.request.user.profile, 
            tienda_id=self.request.data.get('tienda_id')
        )
        
        # Creamos la notificación para el dueño de la tienda
        productos_ids = self.request.data.get('productos_ids', [])
        cantidades = self.request.data.get('cantidades', [])
        
        # Construimos el mensaje detallado de la reserva
        detalles_productos = []
        for producto_id, cantidad in zip(productos_ids, cantidades):
            producto = Producto.objects.get(id=producto_id)
            detalles_productos.append(f"{cantidad}x {producto.nombre}")
        
        productos_texto = ", ".join(detalles_productos)
        
        # Creamos la notificación
        Notificacion.objects.create(
            usuario=reserva.tienda.propietario,
            titulo="Nueva Reserva",
            mensaje=f"El usuario {self.request.user.username} ha realizado una reserva en tu tienda {reserva.tienda.nombre}. "
                   f"Productos reservados: {productos_texto}",
            tipo="nueva_reserva"
        )

    @action(detail=True, methods=['post'], url_path='marcar-retirada')
    def marcar_retirada(self, request, pk=None):
        try:
            reserva = self.get_object()
            if reserva.estado != EstadoReserva.PENDIENTE:
                return Response(
                    {'error': 'Solo se pueden marcar como retiradas las reservas pendientes.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reserva.estado = EstadoReserva.RETIRADO
            reserva.save()
            
            # Notificar al dueño de la tienda
            Notificacion.objects.create(
                usuario=reserva.tienda.propietario,
                titulo="Reserva Marcada como Retirada",
                mensaje=f"El usuario {request.user.username} ha marcado como retirada su reserva en {reserva.tienda.nombre}.",
                tipo="reserva_retirada"
            )
            
            serializer = self.get_serializer(reserva)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error al marcar la reserva como retirada: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar_reserva(self, request, pk=None):
        try:
            reserva = self.get_object()
            if reserva.estado == EstadoReserva.RETIRADO:
                return Response(
                    {'error': 'No se puede cancelar una reserva que ya está retirada.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                # Restaurar el inventario antes de eliminar
                for reserva_producto in reserva.reserva_productos.all():
                    producto = reserva_producto.producto
                    if producto.cantidad_disponible is not None:
                        producto.cantidad_disponible += reserva_producto.cantidad
                        producto.save()
                
                # Notificar al dueño de la tienda
                Notificacion.objects.create(
                    usuario=reserva.tienda.propietario,
                    titulo="Reserva Cancelada",
                    mensaje=f"El usuario {request.user.username} ha cancelado su reserva en {reserva.tienda.nombre}.",
                    tipo="reserva_cancelada"
                )
                
                # Eliminar la reserva
                reserva.delete()

            return Response(
                {'detail': 'Reserva cancelada y eliminada exitosamente.'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Error al cancelar la reserva: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_tiendas(request):
    # Obtener el perfil del usuario autenticado
    profile = request.user.profile
    # Obtener las tiendas asociadas a ese perfil
    tiendas = Tienda.objects.filter(propietario=profile)
    # Serializar las tiendas
    serializer = TiendaSerializer(tiendas, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notificacion
# Add notification endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notificaciones(request):
    notificaciones = Notificacion.objects.filter(usuario=request.user.profile)
    serializer = NotificacionSerializer(notificaciones, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def marcar_notificacion_leida(request, notificacion_id):
    try:
        notificacion = Notificacion.objects.get(id=notificacion_id, usuario=request.user.profile)
        notificacion.leida = True
        notificacion.save()  # Esto activará el signal que eliminará la notificación
        return Response({'status': 'success'})
    except Notificacion.DoesNotExist:
        return Response({'error': 'Notificación no encontrada'}, status=404)