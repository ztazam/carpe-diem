# core/middleware.py
from django.utils import timezone
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class PremiumAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Esto se ejecuta ANTES de que la vista procese la solicitud
        
        # Inicializar como False por defecto
        request.tiene_premium = False
        
        # Verificar si el usuario está autenticado
        if request.user.is_authenticated:
            try:
                # Verificar si existe el perfil de usuario
                if hasattr(request.user, 'perfilusuario'):
                    perfil = request.user.perfilusuario
                    
                    # Verificar acceso premium
                    request.tiene_premium = perfil.tiene_acceso_premium()
                    
                    # Si es premium pero expiró, actualizar estado
                    if (perfil.is_premium and 
                        perfil.premium_expires_at and 
                        timezone.now() > perfil.premium_expires_at):
                        logger.info(f"Premium expirado para usuario: {request.user.username}")
                        perfil.is_premium = False
                        perfil.save()
                        request.tiene_premium = False
                        
                logger.debug(f"Usuario {request.user.username} - Premium: {request.tiene_premium}")
                
            except Exception as e:
                logger.error(f"Error en middleware premium: {str(e)}")
                request.tiene_premium = False

        # Pasar la solicitud al siguiente middleware/vista
        response = self.get_response(request)

        return response