from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tarea
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm
import stripe
from django.conf import settings
from django.http import JsonResponse

def create_payment_intent(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        intent = stripe.PaymentIntent.create(
            amount=1000,  # $10.00 en centavos
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'},
        )
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)})


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_tareas')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('lista_tareas')
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