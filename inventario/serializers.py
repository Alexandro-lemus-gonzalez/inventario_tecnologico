from rest_framework import serializers
from .models import Categoria, Ubicacion, Estado, Activo, Log, Perfil
from django.contrib.auth.models import User

# =========================================
# SERIALIZADORES DE APOYO
# =========================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class UbicacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Ubicacion
        fields = '__all__'


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = '__all__'


# =========================================
# SERIALIZADOR DE ACTIVO (EL PRINCIPAL)
# =========================================

class ActivoSerializer(serializers.ModelSerializer):
    # Campos anidados para lectura (opcional, para ver info completa)
    categoria_detalle = CategoriaSerializer(source='categoria', read_only=True)
    ubicacion_detalle = UbicacionSerializer(source='ubicacion', read_only=True)
    estado_detalle = EstadoSerializer(source='estado', read_only=True)

    class Meta:
        model = Activo
        fields = [
            'id', 'nombre', 'numero_serie', 'codigo_inventario',
            'categoria', 'categoria_detalle',
            'ubicacion', 'ubicacion_detalle',
            'estado', 'estado_detalle',
            'marca', 'modelo', 'descripcion',
            'fecha_adquisicion', 'valor_adquisicion',
            'responsable', 'observaciones', 'foto', 'activo',
            'fecha_registro', 'ultima_actualizacion'
        ]
        # Estos campos son solo de lectura (se llenan automáticamente)
        read_only_fields = ['fecha_registro', 'ultima_actualizacion']


# =========================================
# SERIALIZADOR DE AUDITORÍA
# =========================================

class LogSerializer(serializers.ModelSerializer):
    usuario_detalle = UserSerializer(source='usuario', read_only=True)
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)

    class Meta:
        model = Log
        fields = '__all__'
