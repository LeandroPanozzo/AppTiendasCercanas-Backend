# utils.py - Add a utility function to send notifications
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

# Initialize Firebase Admin SDK
cred_path = os.path.join(settings.BASE_DIR, 'firebase-credentials.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

def enviar_notificacion_fcm(usuario_id, titulo, mensaje, tipo, datos_adicionales=None):
    """
    Envía una notificación a todos los dispositivos de un usuario
    """
    try:
        # Crear la notificación en la base de datos
        from .models import Notificacion, Profile, DeviceToken
        usuario = Profile.objects.get(id=usuario_id)
        
        notificacion = Notificacion.objects.create(
            usuario=usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo
        )
        
        # Obtener los tokens de dispositivo del usuario
        tokens = DeviceToken.objects.filter(usuario=usuario, activo=True).values_list('token', flat=True)
        
        if not tokens:
            return False
        
        # Datos para la notificación
        data = {
            'notificacion_id': str(notificacion.id),
            'tipo': tipo
        }
        
        if datos_adicionales:
            data.update(datos_adicionales)
        
        # Crear el mensaje para FCM
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=titulo,
                body=mensaje
            ),
            data=data,
            tokens=list(tokens)
        )
        
        # Enviar el mensaje
        response = messaging.send_multicast(message)
        print(f'Successfully sent message: {response}')
        
        # Actualizar tokens inválidos
        if response.failure_count > 0:
            for idx, result in enumerate(response.responses):
                if not result.success:
                    # Desactivar token que falló
                    error = result.exception
                    if isinstance(error, messaging.InvalidArgumentError):
                        DeviceToken.objects.filter(token=tokens[idx]).update(activo=False)
        
        return True
    except Exception as e:
        print(f'Error enviando notificación FCM: {e}')
        return False