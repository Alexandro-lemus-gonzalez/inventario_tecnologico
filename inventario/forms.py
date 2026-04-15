""" 
Formularios para la aplicación de inventario. 

Incluye: 
- ActivoForm: Crear y editar activos 
- Validaciones personalizadas 
- Widgets personalizados 
""" 

from django import forms 
from django.core.exceptions import ValidationError 
from .models import Activo, Categoria, Ubicacion, Estado 


class ActivoForm(forms.ModelForm): 
    """ 
    Formulario para crear y editar activos. 
    
    Incluye validaciones personalizadas y widgets Bootstrap. 
    """ 
    
    class Meta: 
        model = Activo 
        fields = [ 
            'codigo_inventario', 
            'nombre', 
            'descripcion', 
            'categoria', 
            'ubicacion', 
            'estado', 
            'marca', 
            'modelo', 
            'numero_serie', 
            'fecha_adquisicion', 
            'valor_adquisicion', 
            'responsable', 
            'observaciones', 
            'foto', 
            'activo', 
        ] 
        
        widgets = { 
            'codigo_inventario': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Ej: ACT-2024-001' 
            }), 
            'nombre': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Nombre del activo' 
            }), 
            'descripcion': forms.Textarea(attrs={ 
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Descripción detallada del activo' 
            }), 
            'categoria': forms.Select(attrs={ 
                'class': 'form-select' 
            }), 
            'ubicacion': forms.Select(attrs={ 
                'class': 'form-select' 
            }), 
            'estado': forms.Select(attrs={ 
                'class': 'form-select' 
            }), 
            'marca': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Ej: HP, Dell, Cisco' 
            }), 
            'modelo': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Modelo específico' 
            }), 
            'numero_serie': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Número de serie único' 
            }), 
            'fecha_adquisicion': forms.DateInput(attrs={ 
                'class': 'form-control', 
                'type': 'date' 
            }), 
            'valor_adquisicion': forms.NumberInput(attrs={ 
                'class': 'form-control', 
                'placeholder': '0.00', 
                'step': '0.01' 
            }), 
            'responsable': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': 'Nombre del responsable' 
            }), 
            'observaciones': forms.Textarea(attrs={ 
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Observaciones adicionales' 
            }), 
            'foto': forms.FileInput(attrs={ 
                'class': 'form-control', 
                'accept': 'image/*' 
            }), 
            'activo': forms.CheckboxInput(attrs={ 
                'class': 'form-check-input' 
            }), 
        } 
        
        labels = { 
            'codigo_inventario': 'Código de Inventario', 
            'nombre': 'Nombre del Activo', 
            'descripcion': 'Descripción', 
            'categoria': 'Categoría', 
            'ubicacion': 'Ubicación', 
            'estado': 'Estado', 
            'marca': 'Marca', 
            'modelo': 'Modelo', 
            'numero_serie': 'Número de Serie', 
            'fecha_adquisicion': 'Fecha de Adquisición', 
            'valor_adquisicion': 'Valor de Adquisición (COP)', 
            'responsable': 'Responsable', 
            'observaciones': 'Observaciones', 
            'foto': 'Fotografía', 
            'activo': '¿Activo en el sistema?', 
        } 
        
        help_texts = { 
            'codigo_inventario': 'Código único que identifica el activo', 
            'numero_serie': 'Número de serie del fabricante', 
            'valor_adquisicion': 'Valor en pesos colombianos', 
            'foto': 'Formatos permitidos: JPG, PNG, WEBP', 
        } 
    
    def __init__(self, *args, **kwargs): 
        """Personalizar el formulario al inicializarse.""" 
        super().__init__(*args, **kwargs) 
        
        # Filtrar solo categorías activas 
        self.fields['categoria'].queryset = Categoria.objects.filter(activa=True) 
        
        # Filtrar solo ubicaciones activas 
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activa=True) 
        
        # Filtrar solo estados activos 
        self.fields['estado'].queryset = Estado.objects.filter(activo=True) 
        
        # Hacer campos opcionales según sea necesario 
        self.fields['ubicacion'].required = False 
        self.fields['descripcion'].required = False 
        self.fields['marca'].required = False 
        self.fields['modelo'].required = False 
        self.fields['numero_serie'].required = False 
        self.fields['fecha_adquisicion'].required = False 
        self.fields['valor_adquisicion'].required = False 
        self.fields['responsable'].required = False 
        self.fields['observaciones'].required = False 
        self.fields['foto'].required = False 
    
    def clean_codigo_inventario(self): 
        """ 
        Validar que el código de inventario tenga el formato correcto. 
        """ 
        codigo = self.cleaned_data.get('codigo_inventario') 
        
        if codigo: 
            # Normalizar a mayúsculas 
            codigo = codigo.strip().upper() 
            
            # Validar formato ACT-YYYY-### 
            if not codigo.startswith('ACT-'): 
                raise ValidationError( 
                    'El código debe empezar con "ACT-" (ejemplo: ACT-2024-001)' 
                ) 
            
            # Verificar que no exista otro activo con el mismo código 
            # (excepto si estamos editando el mismo activo) 
            qs = Activo.objects.filter(codigo_inventario=codigo) 
            if self.instance.pk: 
                qs = qs.exclude(pk=self.instance.pk) 
            
            if qs.exists(): 
                raise ValidationError( 
                    f'Ya existe un activo con el código "{codigo}"' 
                ) 
        
        return codigo 
    
    def clean_numero_serie(self): 
        """Validar que el número de serie sea único.""" 
        numero_serie = self.cleaned_data.get('numero_serie') 
        
        if numero_serie: 
            numero_serie = numero_serie.strip().upper() 
            
            # Verificar unicidad 
            qs = Activo.objects.filter(numero_serie=numero_serie) 
            if self.instance.pk: 
                qs = qs.exclude(pk=self.instance.pk) 
            
            if qs.exists(): 
                raise ValidationError( 
                    f'Ya existe un activo con el número de serie "{numero_serie}"' 
                ) 
        
        return numero_serie 
    
    def clean_valor_adquisicion(self): 
        """Validar que el valor sea positivo.""" 
        valor = self.cleaned_data.get('valor_adquisicion') 
        
        if valor is not None and valor < 0: 
            raise ValidationError('El valor de adquisición no puede ser negativo') 
        
        return valor 
    
    def clean_fecha_adquisicion(self): 
        """Validar que la fecha no sea futura.""" 
        from django.utils import timezone 
        fecha = self.cleaned_data.get('fecha_adquisicion') 
        
        if fecha and fecha > timezone.now().date(): 
            raise ValidationError('La fecha de adquisición no puede ser futura') 
        
        return fecha 
    
    def clean(self): 
        """Validación general del formulario.""" 
        cleaned_data = super().clean() 
        
        # Validar que si hay valor, haya fecha 
        valor = cleaned_data.get('valor_adquisicion') 
        fecha = cleaned_data.get('fecha_adquisicion') 
        
        if valor and not fecha: 
            raise ValidationError( 
                'Si especifica un valor de adquisición, debe indicar la fecha' 
            ) 
        
        return cleaned_data 


""" 
========================================= 
FORMULARIOS DE AUTENTICACIÓN 
========================================= 
""" 

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth.models import User 
from .models import Perfil 


class RegistroForm(UserCreationForm): 
    """Formulario de registro de usuarios.""" 
    
    email = forms.EmailField( 
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'}) 
    ) 
    first_name = forms.CharField( 
        required=True, 
        label='Nombre', 
        widget=forms.TextInput(attrs={'class': 'form-control'}) 
    ) 
    last_name = forms.CharField( 
        required=True, 
        label='Apellido', 
        widget=forms.TextInput(attrs={'class': 'form-control'}) 
    ) 
    
    class Meta: 
        model = User 
        fields = ['username', 'email', 'first_name', 'last_name'] 
        widgets = { 
            'username': forms.TextInput(attrs={'class': 'form-control'}), 
        } 
    
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        # UserCreationForm already has password1 and password2, we just style them
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': 'form-control'}) 
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': 'form-control'}) 
    
    def clean_email(self): 
        """Validar que el email sea único.""" 
        email = self.cleaned_data.get('email') 
        if User.objects.filter(email=email).exists(): 
            raise forms.ValidationError('Este correo ya está registrado.') 
        return email 


class LoginForm(AuthenticationForm): 
    """Formulario de login personalizado.""" 
    
    username = forms.CharField( 
        widget=forms.TextInput(attrs={ 
            'class': 'form-control', 
            'placeholder': 'Usuario' 
        }) 
    ) 
    password = forms.CharField( 
        widget=forms.PasswordInput(attrs={ 
            'class': 'form-control', 
            'placeholder': 'Contraseña' 
        }) 
    ) 


class PerfilForm(forms.ModelForm): 
    """Formulario para editar perfil.""" 
    
    class Meta: 
        model = Perfil 
        fields = ['cargo', 'departamento', 'telefono', 'foto'] 
        widgets = { 
            'cargo': forms.Select(attrs={'class': 'form-select'}), 
            'departamento': forms.Select(attrs={'class': 'form-select'}), 
            'telefono': forms.TextInput(attrs={ 
                'class': 'form-control', 
                'placeholder': '3001234567' 
            }), 
            'foto': forms.FileInput(attrs={ 
                'class': 'form-control', 
                'accept': 'image/*' 
            }), 
        } 


class UserForm(forms.ModelForm): 
    """Formulario para editar datos básicos del usuario.""" 
    
    class Meta: 
        model = User 
        fields = ['first_name', 'last_name', 'email'] 
        widgets = { 
            'first_name': forms.TextInput(attrs={'class': 'form-control'}), 
            'last_name': forms.TextInput(attrs={'class': 'form-control'}), 
            'email': forms.EmailInput(attrs={'class': 'form-control'}), 
        } 
