from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tarea
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Manejar el evento de pago exitoso
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    
    return HttpResponse(status=200)

def handle_checkout_session(session):
    user_id = session.get('client_reference_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile  # Asumiendo que tienes un perfil vinculado
            profile.is_premium = True
            profile.premium_since = timezone.now()
            profile.save()
            
            # Registrar el pago en tu base de datos
            Payment.objects.create(
                user=user,
                stripe_session_id=session['id'],
                amount=session['amount_total'] / 100,
                status='completed'
            )
            
            print(f"✅ Usuario {user.username} actualizado a premium")
            
        except User.DoesNotExist:
            print("❌ Usuario no encontrado")

@csrf_exempt
def create_checkout_session(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Leer el JSON del body si es necesario
        data = json.loads(request.body) if request.body else {}
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Plan Premium CarpeDiem'},
                    'unit_amount': 1000,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://carpe-diem-v4dd.onrender.com/success/',
            cancel_url='https://carpe-diem-v4dd.onrender.com/cancel/',
            client_reference_id=str(request.user.id),
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        print(f"Error en create_checkout_session: {str(e)}")  # Para debug
        return JsonResponse({'error': str(e)}, status=400)

def create_subscription_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_tu_id_de_suscripcion_mensual',  # Obtener de Stripe Dashboard
            'quantity': 1,
        }],
        mode='subscription',  # Modo suscripción, no pago único
        success_url=request.build_absolute_uri('/success/'),
        cancel_url=request.build_absolute_uri('/premium/'),
        client_reference_id=str(request.user.id),
    )
    return JsonResponse({'id': session.id})

def premium(request):
    return render(request, 'core/premium.html', {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def dashboard_premium(request):
    # Verificar si el usuario es premium
    if not hasattr(request.user, 'profile') or not request.user.profile.is_premium:
        return redirect('premium')  # Redirigir a la página de planes
    return render(request, 'core/dashboard_premium.html')

def registro(request):
    # Si el usuario ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        return redirect('lista_tareas')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_tareas')
    else:
        form = RegistroForm()
    
    return render(request, 'core/registro.html', {'form': form})

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Validar que las contraseñas coincidan
            if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                return render(request, 'core/registro.html', {
                    'form': form,
                    'error': 'Las contraseñas no coinciden'
                })
            user = form.save()
            print(f"Usuario {user.username} creado exitosamente")
            login(request, user)
            return redirect('lista_tareas')
        else:
            # Si el formulario no es válido, mostrar errores
            return render(request, 'core/registro.html', {
                'form': form,
                'error': 'Por favor, corrige los errores a continuación.'
            })
    else:
        form = UserCreationForm()
    return render(request, 'core/registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('lista_tareas')
        else:
            return render(request, 'core/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
    return render(request, 'core/login.html')


@login_required
def lista_tareas(request):
    tareas = Tarea.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Calcular estadísticas
    tareas_pendientes = tareas.filter(estado='pendiente').count()
    tareas_completadas = tareas.filter(estado='completada').count()
    total_tareas = tareas.count()
    
    porcentaje_completado = 0
    if total_tareas > 0:
        porcentaje_completado = (tareas_completadas / total_tareas) * 100
    
    context = {
        'tareas': tareas,
        'tareas_pendientes': tareas_pendientes,
        'tareas_completadas': tareas_completadas,
        'porcentaje_completado': round(porcentaje_completado),
    }
    
    return render(request, 'core/lista_tareas.html', context)

@login_required
def crear_tarea(request):
    if request.method=='POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        Tarea.objects.create(usuario=request.user, titulo=titulo, descripcion=descripcion)
        return redirect('lista_tareas')
    return render(request, 'core/crear_tarea.html')

@login_required
def toggle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    tarea.estado = 'completada' if tarea.estado == 'pendiente' else 'pendiente'
    tarea.save()
    return redirect('lista_tareas')

@login_required
def modo_enfoque(request):
    # Obtener la primera tarea pendiente o crear una dummy
    tarea_activa = Tarea.objects.filter(usuario=request.user, estado='pendiente').first()
    
    if not tarea_activa:
        tarea_activa = {
            'titulo': 'No hay tareas pendientes',
            'descripcion': 'Crea una nueva tarea para comenzar'
        }
    
    return render(request, 'core/modo_enfoque.html', {'tarea_activa': tarea_activa})


@login_required
def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    if request.method == 'POST':
        tarea.titulo = request.POST.get('titulo')
        tarea.descripcion = request.POST.get('descripcion')
        tarea.save()
        return redirect('lista_tareas')
    return render(request, 'core/editar_tarea.html', {'tarea': tarea})

@login_required
def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id, usuario=request.user)
    tarea.delete()
    return redirect('lista_tareas')

def success(request):
    return render(request, 'core/success.html')

def cancel(request):
    return render(request, 'core/cancel.html')