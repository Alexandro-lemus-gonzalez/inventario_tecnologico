from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Activo, HistorialMovimiento


@receiver(pre_save, sender=Activo)
def registrar_historial_ubicacion(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        antiguo = Activo.objects.get(pk=instance.pk)

        if antiguo.ubicacion != instance.ubicacion:
            HistorialMovimiento.objects.create(
                activo=instance,
                ubicacion_anterior=antiguo.ubicacion,
                ubicacion_nueva=instance.ubicacion,
                motivo="Cambio automático",
                notas="Movimiento registrado automáticamente por el sistema"
            )

    except Activo.DoesNotExist:
        pass