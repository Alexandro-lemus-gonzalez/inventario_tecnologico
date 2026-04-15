from django.shortcuts import render, get_object_or_404, redirect 
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from django.urls import reverse_lazy 
from django.contrib import messages 
from django.db.models import Count, Sum, Avg, Q 
from django.forms.models import model_to_dict
from django.http import HttpResponse, FileResponse
import json
import os

# Autenticación
from django.contrib.auth import login, logout, authenticate 
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin 
from django.contrib.auth.views import PasswordChangeView 
from django.contrib.auth.forms import PasswordChangeForm 

from .models import ( 
    Activo, Categoria, Ubicacion, Estado, 
    HistorialMovimiento, Mantenimiento, Perfil, Log
) 
from .forms import ActivoForm, RegistroForm, LoginForm, PerfilForm, UserForm 

# Reportes
from .utils.pdf_generator import generar_reporte_inventario_general, generar_reporte_activos_por_ubicacion 
from .utils.excel_generator import exportar_activos_excel, exportar_logs_excel 


# =========================
# DASHBOARD PRINCIPAL
# =========================
@login_required
def dashboard(request):
    """ 
    Dashboard principal del sistema. 
    
    **Protección:** Requiere que el usuario esté autenticado. 
    """ 
    # Total de activos
    total_activos = Activo.objects.filter(activo=True).count()

    # Valor total del inventario
    total_valor = Activo.objects.filter(activo=True).aggregate(
        total=Sum('valor_adquisicion')
    )['total'] or 0

    # Activos por categoría
    categorias = Categoria.objects.annotate(num_activos=Count('activo'))

    # Activos con estado "Mantenimiento" (si existe)
    mantenimientos = Activo.objects.filter(
        estado__nombre__icontains="mantenimiento"
    ).count()

    # Conteo de logs para el dashboard
    total_logs = Log.objects.count()

    context = {
        'total_activos': total_activos,
        'total_valor': total_valor,
        'categorias': categorias,
        'mantenimientos': mantenimientos,
        'total_logs': total_logs
    }

    return render(request, 'inventario/dashboard.html', context)


# ======================================== 
# VISTAS CRUD DE ACTIVOS 
# ======================================== 

class ActivoListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los activos."""
    model = Activo
    template_name = 'inventario/activo_list.html'
    context_object_name = 'activos'
    paginate_by = 10
    login_url = 'inventario:login'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(nombre__icontains=query) | 
                Q(codigo_inventario__icontains=query) |
                Q(numero_serie__icontains=query)
            )
        return queryset.order_by('-fecha_registro')


class ActivoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Vista de detalle de un activo."""
    model = Activo
    template_name = 'inventario/activo_detail.html'
    context_object_name = 'activo'
    permission_required = 'inventario.view_activo'
    login_url = 'inventario:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar historial y mantenimientos al contexto
        context['historial'] = self.object.historial_movimientos.all().order_by('-fecha_movimiento')
        context['mantenimientos'] = self.object.mantenimientos.all().order_by('-fecha_programada')
        
        # Registrar vista en Log
        Log.registrar(
            usuario=self.request.user,
            accion='VIEW',
            modelo='Activo',
            objeto=self.object,
            descripcion=f'Consultó detalle del activo: {self.object.nombre}',
            request=self.request
        )
        return context


class ActivoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView): 
    """Vista para crear un nuevo activo.""" 
    model = Activo 
    form_class = ActivoForm 
    template_name = 'inventario/activo_form.html' 
    success_url = reverse_lazy('inventario:activo_list') 
    permission_required = 'inventario.add_activo'
    login_url = 'inventario:login'
     
    def form_valid(self, form): 
        """Procesar formulario válido.""" 
        response = super().form_valid(form)
        
        # Registrar en Log
        Log.registrar(
            usuario=self.request.user,
            accion='CREATE',
            modelo='Activo',
            objeto=self.object,
            descripcion=f'Creó el activo: {self.object.codigo_inventario}',
            datos_nuevos={
                'codigo_inventario': self.object.codigo_inventario,
                'nombre': self.object.nombre,
                'valor_adquisicion': float(self.object.valor_adquisicion) if self.object.valor_adquisicion else 0,
            },
            request=self.request
        )
        
        messages.success( 
            self.request, 
            f'✓ Activo {self.object.codigo_inventario} creado exitosamente.' 
        ) 
        return response 
     
    def form_invalid(self, form): 
        """Procesar formulario inválido.""" 
        messages.error( 
            self.request, 
            'Error al crear el activo. Por favor revise los campos marcados.' 
        ) 
        return super().form_invalid(form) 


class ActivoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView): 
    """Vista para editar un activo existente.""" 
    model = Activo 
    form_class = ActivoForm 
    template_name = 'inventario/activo_form.html' 
    permission_required = 'inventario.change_activo'
    login_url = 'inventario:login'
     
    def get_success_url(self): 
        """Redirigir al detalle del activo editado.""" 
        return reverse_lazy('inventario:activo_detail', kwargs={'pk': self.object.pk}) 
     
    def form_valid(self, form): 
        """Procesar formulario válido.""" 
        # Obtener datos anteriores
        self.object = self.get_object()
        datos_anteriores = {
            'codigo_inventario': self.object.codigo_inventario,
            'nombre': self.object.nombre,
            'valor_adquisicion': float(self.object.valor_adquisicion) if self.object.valor_adquisicion else 0,
        }
        
        response = super().form_valid(form)
        
        # Registrar en Log
        Log.registrar(
            usuario=self.request.user,
            accion='UPDATE',
            modelo='Activo',
            objeto=self.object,
            descripcion=f'Actualizó el activo: {self.object.codigo_inventario}',
            datos_anteriores=datos_anteriores,
            datos_nuevos={
                'codigo_inventario': self.object.codigo_inventario,
                'nombre': self.object.nombre,
                'valor_adquisicion': float(self.object.valor_adquisicion) if self.object.valor_adquisicion else 0,
            },
            request=self.request
        )
        
        messages.success( 
            self.request, 
            f'Activo "{form.instance.nombre}" actualizado exitosamente.' 
        ) 
        return response 
     
    def form_invalid(self, form): 
        """Procesar formulario inválido.""" 
        messages.error( 
            self.request, 
            'Error al actualizar el activo. Por favor revise los campos marcados.' 
        ) 
        return super().form_invalid(form) 


class ActivoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView): 
    """Vista para eliminar un activo.""" 
    model = Activo 
    template_name = 'inventario/activo_confirm_delete.html' 
    success_url = reverse_lazy('inventario:activo_list') 
    permission_required = 'inventario.delete_activo'
    login_url = 'inventario:login'
     
    def delete(self, request, *args, **kwargs): 
        """Procesar eliminación.""" 
        self.object = self.get_object()
        
        # Registrar en Log ANTES de eliminar
        Log.registrar(
            usuario=self.request.user,
            accion='DELETE',
            modelo='Activo',
            objeto=self.object,
            descripcion=f'Eliminó el activo: {self.object.codigo_inventario}',
            datos_anteriores={
                'codigo_inventario': self.object.codigo_inventario,
                'nombre': self.object.nombre,
                'valor_adquisicion': float(self.object.valor_adquisicion) if self.object.valor_adquisicion else 0,
            },
            request=self.request
        )
        
        messages.success( 
            request, 
            f'Activo "{self.object.nombre}" eliminado exitosamente.' 
        ) 
        return super().delete(request, *args, **kwargs)


# ======================================== 
# VISTAS DE CATEGORÍAS Y UBICACIONES
# ======================================== 

class CategoriaListView(LoginRequiredMixin, ListView):
    """Vista para listar categorías."""
    model = Categoria
    template_name = 'inventario/categoria_list.html'
    context_object_name = 'categorias'
    login_url = 'inventario:login'


class UbicacionListView(LoginRequiredMixin, ListView):
    """Vista para listar ubicaciones."""
    model = Ubicacion
    template_name = 'inventario/ubicacion_list.html'
    context_object_name = 'ubicaciones'
    login_url = 'inventario:login'


# ======================================== 
# VISTAS DE AUTENTICACIÓN 
# ======================================== 

def registro_usuario(request): 
    """Vista para registrar nuevos usuarios.""" 
    if request.user.is_authenticated:
        return redirect('inventario:dashboard')
        
    if request.method == 'POST': 
        form = RegistroForm(request.POST) 
        if form.is_valid(): 
            user = form.save() 
            # Login automático después del registro 
            login(request, user) 
            
            # Log
            Log.registrar(usuario=user, accion='CREATE', modelo='User', objeto=user, descripcion='Nuevo usuario registrado', request=request)
            
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada.') 
            return redirect('inventario:dashboard') 
        else: 
            messages.error(request, 'Por favor corrige los errores del formulario.') 
    else: 
        form = RegistroForm() 
    
    return render(request, 'inventario/registro.html', {'form': form}) 


def login_usuario(request): 
    """Vista para login de usuarios.""" 
    if request.user.is_authenticated: 
        return redirect('inventario:dashboard') 
    
    if request.method == 'POST': 
        form = LoginForm(data=request.POST) 
        if form.is_valid(): 
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password') 
            user = authenticate(username=username, password=password) 
            
            if user is not None: 
                login(request, user)
                
                # Log
                Log.registrar(usuario=user, accion='LOGIN', modelo='User', objeto=user, descripcion='Usuario inició sesión', request=request)
                
                messages.success(request, f'¡Bienvenido {user.username}!') 
                
                # Redirigir a la página que intentaba acceder 
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('inventario:dashboard') 
        else: 
            messages.error(request, 'Usuario o contraseña incorrectos.') 
    else: 
        form = LoginForm() 
    
    return render(request, 'inventario/login.html', {'form': form}) 


@login_required 
def logout_usuario(request): 
    """Vista para cerrar sesión.""" 
    # Log antes de cerrar
    Log.registrar(usuario=request.user, accion='LOGOUT', modelo='User', objeto=request.user, descripcion='Usuario cerró sesión', request=request)
    
    logout(request) 
    messages.info(request, 'Has cerrado sesión correctamente.') 
    return redirect('inventario:login') 


@login_required 
def perfil_usuario(request): 
    """Vista para ver y editar el perfil del usuario.""" 
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST': 
        user_form = UserForm(request.POST, instance=request.user) 
        perfil_form = PerfilForm(request.POST, request.FILES, instance=perfil) 
        
        if user_form.is_valid() and perfil_form.is_valid(): 
            user_form.save() 
            perfil_form.save()
            
            # Log
            Log.registrar(usuario=request.user, accion='UPDATE', modelo='Perfil', objeto=perfil, descripcion='Usuario actualizó su perfil', request=request)
            
            messages.success(request, 'Perfil actualizado correctamente.') 
            return redirect('inventario:perfil_usuario') 
    else: 
        user_form = UserForm(instance=request.user) 
        perfil_form = PerfilForm(instance=perfil) 
    
    context = { 
        'user_form': user_form, 
        'perfil_form': perfil_form, 
    } 
    return render(request, 'inventario/perfil.html', context) 


class CambiarPasswordView(LoginRequiredMixin, PasswordChangeView): 
    """Vista para cambiar contraseña.""" 
    form_class = PasswordChangeForm 
    template_name = 'inventario/cambiar_password.html' 
    success_url = reverse_lazy('inventario:perfil_usuario') 
    login_url = 'inventario:login'
    
    def form_valid(self, form): 
        # Log
        Log.registrar(usuario=self.request.user, accion='UPDATE', modelo='User', objeto=self.request.user, descripcion='Usuario cambió su contraseña', request=self.request)
        
        messages.success(self.request, 'Contraseña cambiada correctamente.') 
        return super().form_valid(form) 


# ======================================== 
# VISTAS PARA AUDITORÍA (LOGS)
# ======================================== 

class LogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Vista para listar logs de auditoría."""
    model = Log
    template_name = 'inventario/log_list.html'
    context_object_name = 'logs'
    paginate_by = 20
    permission_required = 'inventario.view_log'
    login_url = 'inventario:login'

    def get_queryset(self):
        queryset = super().get_queryset()
        accion = self.request.GET.get('accion')
        usuario = self.request.GET.get('usuario')
        if accion:
            queryset = queryset.filter(accion=accion)
        if usuario:
            queryset = queryset.filter(usuario_nombre__icontains=usuario)
        return queryset


class LogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Vista de detalle de un log."""
    model = Log
    template_name = 'inventario/log_detail.html'
    context_object_name = 'log'
    permission_required = 'inventario.view_log'
    login_url = 'inventario:login'


# ======================================== 
# VISTAS PARA REPORTES PDF Y EXCEL
# ======================================== 

@login_required 
@permission_required('inventario.view_activo', raise_exception=True) 
def reporte_inventario_pdf(request): 
    """Generar reporte PDF de inventario general.""" 
    try: 
        activos = Activo.objects.filter(activo=True).select_related( 
            'categoria', 'ubicacion', 'estado' 
        ) 
        pdf_path = generar_reporte_inventario_general(activos) 
        Log.registrar( 
            usuario=request.user, 
            accion='EXPORT', 
            modelo='Activo', 
            descripcion='Generó reporte PDF de inventario general', 
            request=request 
        ) 
        return FileResponse( 
            open(pdf_path, 'rb'), 
            content_type='application/pdf', 
            as_attachment=True, 
            filename=os.path.basename(pdf_path) 
        ) 
    except Exception as e: 
        messages.error(request, f'Error al generar reporte PDF: {str(e)}')
        return redirect('inventario:activo_list')


@login_required
@permission_required('inventario.view_activo', raise_exception=True)
def exportar_activos_excel_view(request):
    """Exportar listado de activos a Excel."""
    try:
        activos = Activo.objects.all().select_related('categoria', 'ubicacion', 'estado')
        excel_path = exportar_activos_excel(activos)
        Log.registrar(
            usuario=request.user,
            accion='EXPORT',
            modelo='Activo',
            descripcion='Exportó activos a Excel',
            request=request
        )
        return FileResponse(
            open(excel_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            filename=os.path.basename(excel_path)
        )
    except Exception as e:
        messages.error(request, f'Error al exportar Excel: {str(e)}')
        return redirect('inventario:activo_list')


@login_required
@permission_required('inventario.view_log', raise_exception=True)
def exportar_auditoria_excel_view(request):
    """Exportar logs de auditoría a Excel."""
    try:
        logs = Log.objects.all()
        excel_path = exportar_logs_excel(logs)
        Log.registrar(
            usuario=request.user,
            accion='EXPORT',
            modelo='Log',
            descripcion='Exportó logs de auditoría a Excel',
            request=request
        )
        return FileResponse(
            open(excel_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            filename=os.path.basename(excel_path)
        )
    except Exception as e:
        messages.error(request, f'Error al exportar logs: {str(e)}')
        return redirect('inventario:dashboard')
