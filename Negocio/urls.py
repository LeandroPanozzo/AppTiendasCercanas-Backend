from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, TiendaViewSet,
    ProductoViewSet, ReservaViewSet, mis_tiendas, 
    get_notificaciones, marcar_notificacion_leida # Importar la nueva vista de google_auth
)

# Crear router y registrar vistas
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'tiendas', TiendaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'reservas', ReservaViewSet)

# Incluir el router y todas las vistas
urlpatterns = [
    path('', include(router.urls)),
    path('mis-tiendas/', mis_tiendas, name='mis_tiendas'),
    path('notificaciones/', get_notificaciones, name='notificaciones'),
    path('notificaciones/<int:notificacion_id>/leida/', marcar_notificacion_leida, name='marcar-leida'),

]