from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Categoria,
    Ubicacion,
    Estado,
    Activo,
    HistorialMovimiento,
    Mantenimiento
)

# =========================
# CATEGORÍA
# =========================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


# =========================
# UBICACIÓN
# =========================
@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


# =========================
# ESTADO
# =========================
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'color_hex', 'permite_prestamo', 'visible_en_reportes')
    list_filter = ('permite_prestamo', 'visible_en_reportes')
    search_fields = ('nombre',)


# =========================
# ACTIVO (MODELO PRINCIPAL)
# =========================
@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):

    fieldsets = (
        ('📌 Información Básica', {
            'fields': ('nombre', 'numero_serie', 'codigo_inventario', 'imagen')
        }),
        ('🏷️ Clasificación', {
            'fields': ('categoria', 'ubicacion', 'estado')
        }),
        ('🛠️ Detalles Técnicos', {
            'fields': ('marca', 'modelo', 'descripcion')
        }),
        ('💰 Compra', {
            'fields': ('fecha_compra', 'precio')
        }),
    )

    list_display = (
        'codigo_inventario',
        'nombre',
        'categoria',
        'ubicacion',
        'estado',
        'ver_foto'
    )

    list_filter = ('categoria', 'ubicacion', 'estado', 'marca')
    search_fields = ('nombre', 'numero_serie', 'codigo_inventario')

    def ver_foto(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;border-radius:6px;" />',
                obj.imagen.url
            )
        return "Sin imagen"

    ver_foto.short_description = "Foto"


# =========================
# HISTORIAL DE MOVIMIENTOS (SESIÓN 5)
# =========================
@admin.register(HistorialMovimiento)
class HistorialMovimientoAdmin(admin.ModelAdmin):
    list_display = (
        'activo',
        'ubicacion_anterior',
        'ubicacion_nueva',
        'fecha_movimiento',
        'usuario'
    )

    list_filter = ('fecha_movimiento', 'ubicacion_nueva')
    search_fields = ('activo__nombre', 'motivo')
    readonly_fields = ('fecha_movimiento',)


# =========================
# MANTENIMIENTO (SESIÓN 5)
# =========================
@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):

    list_display = (
        'activo',
        'tipo',
        'fecha_programada',
        'fecha_realizada',
        'completado',
        'costo'
    )

    list_filter = ('tipo', 'completado')
    search_fields = ('activo__nombre', 'tecnico_responsable')


""" 
========================================= 
ADMIN PERFIL DE USUARIO 
========================================= 
""" 

from django.contrib.auth.models import User 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from .models import Perfil


class PerfilInline(admin.StackedInline): 
    """Inline para mostrar perfil en el admin de User.""" 
    model = Perfil 
    can_delete = False 
    verbose_name = 'Perfil' 
    verbose_name_plural = 'Perfiles' 
    
    fieldsets = ( 
        ('Información Laboral', { 
            'fields': ('cargo', 'departamento', 'telefono') 
        }), 
        ('Multimedia', { 
            'fields': ('foto',) 
        }), 
    ) 


class UserAdmin(BaseUserAdmin): 
    """Admin personalizado para User con Perfil inline.""" 
    inlines = (PerfilInline,) 


# Re-registrar UserAdmin 
admin.site.unregister(User) 
admin.site.register(User, UserAdmin)


""" 
========================================= 
ADMIN LOG DE AUDITORÍA 
========================================= 
""" 

from .models import Log


@admin.register(Log) 
class LogAdmin(admin.ModelAdmin): 
    """Admin para visualizar logs de auditoría.""" 
     
    list_display = [ 
        'fecha_hora', 
        'usuario_nombre', 
        'accion', 
        'modelo', 
        'objeto_repr', 
        'ip_address' 
    ] 
     
    list_filter = [ 
        'accion', 
        'modelo', 
        'fecha_hora', 
    ] 
     
    search_fields = [ 
        'usuario_nombre', 
        'descripcion', 
        'objeto_repr', 
    ] 
     
    readonly_fields = [ 
        'usuario', 
        'usuario_nombre', 
        'accion', 
        'modelo', 
        'objeto_id', 
        'objeto_repr', 
        'fecha_hora', 
        'descripcion', 
        'datos_anteriores', 
        'datos_nuevos', 
        'ip_address', 
        'user_agent', 
    ] 
     
    def has_add_permission(self, request): 
        """Los logs no se crean manualmente.""" 
        return False 
     
    def has_delete_permission(self, request, obj=None): 
        """Los logs no se eliminan (por auditoría).""" 
        return False 
     
    def has_change_permission(self, request, obj=None): 
        """Los logs son read-only.""" 
        return False