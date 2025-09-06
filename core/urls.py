from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.lista_tareas, name='lista_tareas'),
    path('crear/', views.crear_tarea, name='crear_tarea'),
    path('toggle/<int:tarea_id>/', views.toggle_tarea, name='toggle_tarea'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', LogoutView.as_view(template_name='core/logout.html'), name='logout'),
    path('enfoque/', views.modo_enfoque, name='modo_enfoque'),
    path('editar/<int:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('eliminar/<int:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('premium/', views.premium, name='premium'),
]