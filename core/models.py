from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    premium_since = models.DateTimeField(null=True, blank=True)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    
    def tiene_acceso_premium(self):
        """Verifica si el usuario tiene acceso premium activo"""
        if self.is_premium and self.premium_expires_at:
            return timezone.now() < self.premium_expires_at
        return self.is_premium
    
    def activar_premium(self, dias=30):
        """Activa la suscripción premium por X días"""
        self.is_premium = True
        self.premium_since = timezone.now()
        self.premium_expires_at = timezone.now() + timezone.timedelta(days=dias)
        self.save()
        return True
    
    def __str__(self):
        return f"Perfil de {self.user.username} - Premium: {self.is_premium}" 

class Tarea(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('conmpletada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=11, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
          return self.titulo

class ResumenDiario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    tareas_completadas = models.IntegerField(default=0)
    tiempo_enfoque = models.IntegerField(default=0) #En minutos
    notas = models.TextField(blank=True)

    class Meta:
        unique_together = ['usuario', 'fecha'] #un resumen por usuario por dia
        
    def __str__(self):
        return f"Resumen de {self.usuario.username} - {self.fecha}"    

    @receiver(post_save, sender=User)
    def crear_perfil_usuario(sender, instance, created, **kwargs):
        if created:
            
            PerfilUsuario.objects.create(user=instance)

    #@receiver(post_save, sender=User)
    #def guardar_perfil_usuario(sender, instance, **kwargs):
    
    #  instance.perfilusuario.save()

    @receiver(post_save, sender=User)
    def guardar_perfil_usuario(sender, instance, **kwargs):
        if hasattr(instance, 'profile'):
            instance.profile.save()