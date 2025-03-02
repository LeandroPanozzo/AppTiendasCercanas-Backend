from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    DeviceToken, Profile, ReservaProducto, Tienda, Producto, Reserva, CategoriaTiendaChoices, 
    DiasAtencionChoices
)
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
# serializers.py
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}  # Para que no se pueda modificar el username
        }

    def validate(self, attrs):
        # Validar que las contraseñas coincidan
        if 'password' in attrs:
            if attrs['password'] != attrs.pop('password2', None):
                raise serializers.ValidationError("Las contraseñas no coinciden.")

        # Validar que el correo electrónico no esté en uso
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este correo electrónico ya está en uso.")

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        Profile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        # Actualizar solo los campos permitidos
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = (
            'id', 'user', 'tiene_comercio',
            'direccion_calle', 'direccion_numero', 'ciudad', 'provincia',
            'coordenada_latitud', 'coordenada_longitud', 'rango_busqueda_km'
        )
        read_only_fields = ('id', 'coordenada_latitud', 'coordenada_longitud')

    def update(self, instance, validated_data):
        # Manejar la actualización del usuario si se proporcionan datos
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer()
            user_serializer.update(instance.user, user_data)

        # Manejar la actualización del perfil sin requerir el campo 'pais'
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance


class TiendaSerializer(serializers.ModelSerializer):
    propietario = ProfileSerializer(read_only=True)
    whatsapp_link = serializers.SerializerMethodField()
    logo = serializers.ImageField(write_only=True, required=False)
    
    class Meta:
        model = Tienda
        fields = (
            'id', 'nombre', 'url_logo', 'logo', 'provincia', 'ciudad', 'descripcion',
            'direccion_calle', 'direccion_numero', 'categoria', 'dias_atencion',
            'horario_apertura', 'horario_cierre', 'propietario', 
            # Payment method boolean fields
            'efectivo', 'debito', 'credito', 'transferencia_bancaria', 
            'pago_movil', 'qr', 'monedero_electronico', 'criptomoneda', 
            'pasarela_en_linea', 'cheque', 'pagos_a_plazos', 'vales', 
            'contra_entrega', 'debito_directo', 'creditos_internos',
            'coordenada_latitud', 'coordenada_longitud', 
            'whatsapp', 'whatsapp_link'
        )
        read_only_fields = ('url_logo',)
        extra_kwargs = {
            'nombre': {'required': False},
            'direccion_calle': {'required': False},
            'direccion_numero': {'required': False},
            'horario_apertura': {'required': False},
            'horario_cierre': {'required': False},
            'provincia': {'required': True},
            'whatsapp': {'required': False},
        }

    def get_whatsapp_link(self, obj):
        return obj.obtener_link_whatsapp()

    def create(self, validated_data):
        validated_data['propietario'] = self.context['request'].user.profile
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(f"Datos del whatsapp en serializer: {instance.whatsapp}")
        return data

class ProductoSerializer(serializers.ModelSerializer):
    tienda = TiendaSerializer(read_only=True)
    tienda_id = serializers.IntegerField(write_only=True)
    imagen = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Producto
        fields = (
            'id', 'tienda', 'tienda_id', 'categoria', 'nombre', 'url_imagen',
            'estado_publicacion', 'disponibilidad', 'descripcion', 'precio',
            'precio_original', 'porcentaje_descuento', 'cantidad_disponible',
            'es_servicio', 'permite_reservas', 'imagen', 'promocion_nx', 'fecha_creacion',
            'promocion_porcentaje', 'promocion_unidad'
        )
        read_only_fields = ('url_imagen', 'precio_original', 'porcentaje_descuento', 'fecha_creacion')

    def create(self, validated_data):
        imagen = validated_data.pop('imagen', None)
        instance = super().create(validated_data)
        # Manejo de la imagen si es necesario
        return instance

    def validate(self, data):
        if data.get('es_servicio') and data.get('cantidad_disponible') is not None:
            raise serializers.ValidationError({
                'cantidad_disponible': 'Este campo debe estar vacío si el producto es un servicio.'
            })
        # Validación de promociones
        promocion_nx = data.get('promocion_nx')
        promocion_porcentaje = data.get('promocion_porcentaje')
        promocion_unidad = data.get('promocion_unidad')
        
        if promocion_nx:
            import re
            if not re.match(r'^\d+x\d+$', promocion_nx):
                raise serializers.ValidationError({
                    'promocion_nx': 'El formato debe ser "NxM" (ejemplo: "2x1", "3x2")'
                })
        
        if (promocion_porcentaje is not None and promocion_unidad is None) or \
           (promocion_porcentaje is None and promocion_unidad is not None):
            raise serializers.ValidationError(
                'Debe especificar tanto el porcentaje como la unidad para la promoción porcentual'
            )
            
        if promocion_porcentaje is not None and \
           (promocion_porcentaje < 0 or promocion_porcentaje > 100):
            raise serializers.ValidationError({
                'promocion_porcentaje': 'El porcentaje debe estar entre 0 y 100'
            })
        
        return data


class ReservaSerializer(serializers.ModelSerializer):
    usuario = ProfileSerializer(read_only=True)
    tienda = TiendaSerializer(read_only=True)
    productos = ProductoSerializer(many=True, read_only=True)
    reserva_productos = serializers.SerializerMethodField()
    estado = serializers.CharField(read_only=True)  # Agregamos esto explícitamente
    productos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    cantidades = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=True
    )
    tienda_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reserva
        fields = ('id', 'usuario', 'tienda', 'tienda_id', 'productos', 
                 'productos_ids', 'cantidades', 'fecha_reserva', 
                 'reserva_productos', 'estado')  # Agregamos estado aquí también

    def get_reserva_productos(self, obj):
        return [
            {
                'producto': rp.producto_id,
                'cantidad': rp.cantidad,
            }
            for rp in obj.reserva_productos.all()
        ]
    def validate(self, data):
        if len(data['productos_ids']) != len(data['cantidades']):
            raise serializers.ValidationError("La cantidad de productos y cantidades debe ser la misma")
        return data

    def create(self, validated_data):
        productos_ids = validated_data.pop('productos_ids')
        cantidades = validated_data.pop('cantidades')
        
        reserva = super().create(validated_data)
        
        for producto_id, cantidad in zip(productos_ids, cantidades):
            producto = Producto.objects.get(id=producto_id)
            
            if not producto.disponibilidad or producto.es_servicio:
                reserva.delete()
                raise serializers.ValidationError(f"El producto '{producto.nombre}' no está disponible para reserva.")
            
            if producto.cantidad_disponible is not None and cantidad > producto.cantidad_disponible:
                reserva.delete()
                raise serializers.ValidationError(
                    f"No hay suficiente cantidad disponible para el producto '{producto.nombre}'."
                )
            
            ReservaProducto.objects.create(
                reserva=reserva,
                producto=producto,
                cantidad=cantidad
            )
        
        return reserva
from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'titulo', 'mensaje', 'leida', 'fecha_creacion', 'tipo']
# serializers.py - Add this to your serializers
class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['token']