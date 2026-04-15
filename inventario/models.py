import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# =========================
# VALIDACIONES
# =========================

def validar_nombre_categoria(value):
    if len(value) < 4:
        raise ValidationError("El nombre debe tener al menos 4 caracteres.")

def validar_color_hex(value):
    reg = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not re.match(reg, value):
        raise ValidationError("Color hexadecimal inválido.")


# =========================
# CATEGORÍA
# =========================

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, validators=[validar_nombre_categoria])
    codigo = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


# =========================
# UBICACIÓN
# =========================

class Ubicacion(models.Model):
    TIPO_CHOICES = [
        ('BOD', 'Bodega'),
        ('LAB', 'Laboratorio'),
        ('OFI', 'Oficina'),
        ('SAL', 'Sala de Sistemas'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    piso = models.IntegerField(default=1)
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, default='OFI')
    capacidad_maxima = models.PositiveIntegerField()

    es_externa = models.BooleanField(default=False)
    responsable = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    email_contacto = models.EmailField(null=True, blank=True)

    observaciones = models.TextField(blank=True)

    # 🔥 CAMBIO IMPORTANTE
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"


# =========================
# ESTADO
# =========================

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color_hex = models.CharField(max_length=7, validators=[validar_color_hex], default="#39A900")
    descripcion = models.TextField(blank=True)
    permite_prestamo = models.BooleanField(default=True)
    es_critico = models.BooleanField(default=False)
    prioridad = models.IntegerField(default=1)
    abreviatura = models.CharField(max_length=5, blank=True, null=True)
    requiere_mantenimiento = models.BooleanField(default=False)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    visible_en_reportes = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    icon_name = models.CharField(max_length=30, default="check-circle")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"


# =========================
# ACTIVO
# =========================

class Activo(models.Model):
    nombre = models.CharField(max_length=150)
    numero_serie = models.CharField(max_length=100, unique=True, null=True, blank=True)
    codigo_inventario = models.CharField(max_length=50, unique=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='activos')

    marca = models.CharField(max_length=100, null=True, blank=True)
    modelo = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    fecha_adquisicion = models.DateField(null=True, blank=True)
    valor_adquisicion = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    responsable = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='activos/%Y/%m/', null=True, blank=True)
    activo = models.BooleanField(default=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.codigo_inventario}"

    class Meta:
        verbose_name = "Activo"
        verbose_name_plural = "Activos"


# =========================
# HISTORIAL MOVIMIENTOS
# =========================

class HistorialMovimiento(models.Model):
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='historial_movimientos')
    ubicacion_anterior = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, related_name='salidas')
    ubicacion_nueva = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, related_name='entradas')
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.activo.nombre} - {self.fecha_movimiento}"

    class Meta:
        verbose_name = "Historial de Movimiento"
        verbose_name_plural = "Historial de Movimientos"


# =========================
# MANTENIMIENTO
# =========================

class Mantenimiento(models.Model):
    TIPO_MANT_CHOICES = [
        ('PREV', 'Preventivo'),
        ('CORR', 'Correctivo'),
        ('GAR', 'Garantía'),
    ]

    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='mantenimientos')

    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(null=True, blank=True)

    tipo = models.CharField(max_length=4, choices=TIPO_MANT_CHOICES)

    tecnico_responsable = models.CharField(max_length=150)
    descripcion_problema = models.TextField()
    tareas_realizadas = models.TextField(blank=True)

    repuestos_cambiados = models.TextField(blank=True)

    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    proximo_mantenimiento = models.DateField(null=True, blank=True)

    completado = models.BooleanField(default=False)

    adjunto_reporte = models.FileField(upload_to='mantenimientos/pdfs/', null=True, blank=True)

    def __str__(self):
        return f"{self.activo.nombre} - {self.tipo}"

    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"


""" 
========================================= 
MODELO DE PERFIL DE USUARIO 
========================================= 
""" 

from django.db.models.signals import post_save 
from django.dispatch import receiver 


class Perfil(models.Model): 
    """ 
    Perfil extendido de usuario. 
    
    Extiende el modelo User de Django con información adicional 
    específica del sistema de inventario. 
    """ 
    
    CARGOS = [ 
        ('ADMIN', 'Administrador'), 
        ('COORD', 'Coordinador'), 
        ('TEC', 'Técnico'), 
        ('AUX', 'Auxiliar'), 
    ] 
    
    DEPARTAMENTOS = [ 
        ('TI', 'Tecnología e Informática'), 
        ('ADM', 'Administrativo'), 
        ('MTO', 'Mantenimiento'), 
        ('LOG', 'Logística'), 
    ] 
    
    usuario = models.OneToOneField( 
        User, 
        on_delete=models.CASCADE, 
        related_name='perfil' 
    ) 
    cargo = models.CharField( 
        max_length=10, 
        choices=CARGOS, 
        default='AUX' 
    ) 
    departamento = models.CharField( 
        max_length=10, 
        choices=DEPARTAMENTOS, 
        default='TI' 
    ) 
    telefono = models.CharField( 
        max_length=20, 
        blank=True, 
        null=True 
    ) 
    foto = models.ImageField( 
        upload_to='perfiles/', 
        blank=True, 
        null=True 
    ) 
    fecha_creacion = models.DateTimeField(auto_now_add=True) 
    fecha_modificacion = models.DateTimeField(auto_now=True) 
    
    class Meta: 
        verbose_name = 'Perfil' 
        verbose_name_plural = 'Perfiles' 
        ordering = ['usuario__username'] 
    
    def __str__(self): 
        return f"Perfil de {self.usuario.username}" 
    
    def get_nombre_completo(self): 
        """Obtener nombre completo del usuario.""" 
        if self.usuario.first_name and self.usuario.last_name: 
            return f"{self.usuario.first_name} {self.usuario.last_name}" 
        return self.usuario.username 


# Señales para crear/actualizar perfil automáticamente 
@receiver(post_save, sender=User) 
def crear_perfil_usuario(sender, instance, created, **kwargs): 
    """Crear perfil automáticamente cuando se crea un usuario.""" 
    if created: 
        Perfil.objects.create(usuario=instance) 


@receiver(post_save, sender=User) 
def guardar_perfil_usuario(sender, instance, **kwargs): 
    """Guardar perfil cuando se guarda el usuario.""" 
    try:
        instance.perfil.save()
    except Perfil.DoesNotExist:
        Perfil.objects.create(usuario=instance)


""" 
========================================= 
MODELO DE AUDITORÍA (LOG) 
========================================= 
""" 


class Log(models.Model): 
    """ 
    Registro de auditoría del sistema. 
     
    Registra todas las acciones importantes que ocurren en el sistema 
    para mantener trazabilidad completa. 
    """ 
     
    ACCIONES = [ 
        ('CREATE', 'Crear'), 
        ('UPDATE', 'Actualizar'), 
        ('DELETE', 'Eliminar'), 
        ('VIEW', 'Ver'), 
        ('LOGIN', 'Iniciar Sesión'), 
        ('LOGOUT', 'Cerrar Sesión'), 
        ('EXPORT', 'Exportar'), 
        ('IMPORT', 'Importar'), 
    ] 
     
    # Quien 
    usuario = models.ForeignKey( 
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='logs' 
    ) 
    usuario_nombre = models.CharField( 
        max_length=150, 
        help_text='Nombre del usuario (guardado para histórico)' 
    ) 
     
    # Qué 
    accion = models.CharField(max_length=20, choices=ACCIONES) 
    modelo = models.CharField( 
        max_length=100, 
        help_text='Nombre del modelo afectado (ej: Activo, Categoria)' 
    ) 
    objeto_id = models.CharField( 
        max_length=100, 
        blank=True, 
        null=True, 
        help_text='ID del objeto afectado' 
    ) 
    objeto_repr = models.CharField( 
        max_length=200, 
        blank=True, 
        help_text='Representación del objeto' 
    ) 
     
    # Cuándo 
    fecha_hora = models.DateTimeField(auto_now_add=True) 
     
    # Detalles 
    descripcion = models.TextField( 
        blank=True, 
        help_text='Descripción detallada de la acción' 
    ) 
    datos_anteriores = models.JSONField( 
        null=True, 
        blank=True, 
        help_text='Estado antes del cambio (JSON)' 
    ) 
    datos_nuevos = models.JSONField( 
        null=True, 
        blank=True, 
        help_text='Estado después del cambio (JSON)' 
    ) 
     
    # Contexto técnico 
    ip_address = models.GenericIPAddressField( 
        null=True, 
        blank=True, 
        help_text='Dirección IP del usuario' 
    ) 
    user_agent = models.CharField( 
        max_length=255, 
        blank=True, 
        help_text='Navegador y sistema operativo' 
    ) 
     
    class Meta: 
        verbose_name = 'Log' 
        verbose_name_plural = 'Logs' 
        ordering = ['-fecha_hora'] 
        indexes = [ 
            models.Index(fields=['-fecha_hora']), 
            models.Index(fields=['usuario', '-fecha_hora']), 
            models.Index(fields=['modelo', '-fecha_hora']), 
        ] 
     
    def __str__(self): 
        return f"{self.usuario_nombre} - {self.get_accion_display()} - {self.modelo} - {self.fecha_hora}" 
     
    @classmethod 
    def registrar(cls, usuario, accion, modelo, objeto=None, descripcion='',  
                  datos_anteriores=None, datos_nuevos=None, request=None): 
        """ 
        Método auxiliar para crear logs fácilmente. 
        """ 
        log = cls( 
            usuario=usuario if usuario and usuario.is_authenticated else None, 
            usuario_nombre=usuario.username if usuario and usuario.is_authenticated else 'Anónimo', 
            accion=accion, 
            modelo=modelo, 
            descripcion=descripcion, 
            datos_anteriores=datos_anteriores, 
            datos_nuevos=datos_nuevos, 
        ) 
         
        if objeto: 
            log.objeto_id = str(objeto.pk) 
            log.objeto_repr = str(objeto) 
         
        if request: 
            # Obtener IP 
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR') 
            if x_forwarded_for: 
                log.ip_address = x_forwarded_for.split(',')[0] 
            else: 
                log.ip_address = request.META.get('REMOTE_ADDR') 
             
            # Obtener User Agent 
            log.user_agent = request.META.get('HTTP_USER_AGENT', '')[:255] 
         
        log.save() 
        return log