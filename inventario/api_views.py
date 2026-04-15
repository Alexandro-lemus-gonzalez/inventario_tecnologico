from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum
from .models import Activo, Categoria, Ubicacion, Estado, Log
from .serializers import (
    ActivoSerializer, CategoriaSerializer, 
    UbicacionSerializer, EstadoSerializer, LogSerializer
)

# =========================================
# VIEWSETS (CONTROLADORES DE LA API)
# =========================================

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    Endpoint para ver, crear, editar y eliminar categorías.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['activa']
    search_fields = ['nombre', 'codigo']


class UbicacionViewSet(viewsets.ModelViewSet):
    """
    Endpoint para ver, crear, editar y eliminar ubicaciones.
    """
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['tipo', 'activa']
    search_fields = ['nombre', 'responsable']


class EstadoViewSet(viewsets.ModelViewSet):
    """
    Endpoint para ver, crear, editar y eliminar estados.
    """
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActivoViewSet(viewsets.ModelViewSet):
    """
    Endpoint principal para la gestión de activos.
    """
    queryset = Activo.objects.all()
    serializer_class = ActivoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configuración de filtros y búsqueda
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'ubicacion', 'estado', 'activo']
    search_fields = ['nombre', 'codigo_inventario', 'numero_serie', 'marca', 'modelo']
    ordering_fields = ['fecha_adquisicion', 'valor_adquisicion', 'fecha_registro']

    # ACCIONES PERSONALIZADAS (Para el Dashboard)
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas para los gráficos del dashboard de forma eficiente.
        """
        por_categoria = Activo.objects.values('categoria__nombre').annotate(total=Count('id'))
        por_estado = Activo.objects.values('estado__nombre', 'estado__color_hex').annotate(total=Count('id'))
        
        # Uso de aggregate(Sum) para mejorar el rendimiento (Evita el bucle en Python)
        total_valor_dict = Activo.objects.aggregate(total_valor=Sum('valor_adquisicion'))
        
        return Response({
            'por_categoria': por_categoria,
            'por_estado': por_estado,
            'total_activos': Activo.objects.count(),
            'total_valor': total_valor_dict['total_valor'] or 0.00
        })


class LogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de solo lectura para consultar la auditoría.
    """
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['accion', 'modelo', 'usuario']
    search_fields = ['descripcion', 'objeto_repr', 'usuario_nombre']
