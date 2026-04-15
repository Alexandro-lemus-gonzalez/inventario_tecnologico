""" 
URLs para la aplicación de inventario. 
""" 

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'inventario'

# =========================================
# CONFIGURACIÓN DEL ROUTER (API)
# =========================================
router = DefaultRouter()
router.register(r'activos', api_views.ActivoViewSet, basename='api-activos')
router.register(r'categorias', api_views.CategoriaViewSet, basename='api-categorias')
router.register(r'ubicaciones', api_views.UbicacionViewSet, basename='api-ubicaciones')
router.register(r'estados', api_views.EstadoViewSet, basename='api-estados')
router.register(r'logs', api_views.LogViewSet, basename='api-logs')

urlpatterns = [
    # Dashboard (En la raíz)
    path('', views.dashboard, name='dashboard'),

    # API ENDPOINTS (Bajo el prefijo /api/)
    path('api/', include(router.urls)),
    
    # Activos - CRUD completo 
    path('activos/', views.ActivoListView.as_view(), name='activo_list'), 
    path('activos/crear/', views.ActivoCreateView.as_view(), name='activo_create'), 
    path('activos/<int:pk>/', views.ActivoDetailView.as_view(), name='activo_detail'), 
    path('activos/<int:pk>/editar/', views.ActivoUpdateView.as_view(), name='activo_update'), 
    path('activos/<int:pk>/eliminar/', views.ActivoDeleteView.as_view(), name='activo_delete'), 
    
    # Categorías 
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'), 
    
    # Ubicaciones 
    path('ubicaciones/', views.UbicacionListView.as_view(), name='ubicacion_list'), 

    # Autenticación 
    path('registro/', views.registro_usuario, name='registro'), 
    path('login/', views.login_usuario, name='login'), 
    path('logout/', views.logout_usuario, name='logout'), 
    path('perfil/', views.perfil_usuario, name='perfil_usuario'), 
    path('password-change/', views.CambiarPasswordView.as_view(), name='password_change'), 

    # Auditoría (Logs)
    path('logs/', views.LogListView.as_view(), name='log_list'),
    path('logs/<int:pk>/', views.LogDetailView.as_view(), name='log_detail'),

    # Reportes
    path('reportes/inventario-pdf/', views.reporte_inventario_pdf, name='reporte_inventario_pdf'),
    path('reportes/activos-excel/', views.exportar_activos_excel_view, name='exportar_activos_excel'),
    path('reportes/auditoria-excel/', views.exportar_auditoria_excel_view, name='exportar_auditoria_excel'),
] 
