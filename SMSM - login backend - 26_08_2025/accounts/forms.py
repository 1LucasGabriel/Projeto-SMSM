from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from demands.models import HealthUnit 

class CustomUserCreationForm(UserCreationForm):
    """
    Formulário para criação de novos usuários (utilizado pelo Admin Global e Admin Local).
    Inclui campos personalizados como user_type, professional_registration, cpf e health_unit.
    """
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('user_type', 'professional_registration', 'cpf', 'health_unit',)

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop('request_user', None)
        super().__init__(*args, **kwargs)

        if self.request_user and self.request_user.user_type == 'admin_local':
            self.fields['health_unit'].queryset = HealthUnit.objects.filter(pk=self.request_user.health_unit.pk)
            self.fields['health_unit'].initial = self.request_user.health_unit
            self.fields['health_unit'].disabled = True 

    def clean_professional_registration(self):
        professional_registration = self.cleaned_data.get('professional_registration')
        if professional_registration and get_user_model().objects.filter(professional_registration = professional_registration).exists():
            raise forms.ValidationError("Este Registro Profissional já está em uso.")
        return professional_registration
        
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if get_user_model().objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Este CPF já está em uso.")
        return cpf

    def clean_health_unit(self):
        health_unit = self.cleaned_data.get('health_unit')
        if self.request_user and self.request_user.user_type == 'admin_local':
            if health_unit != self.request_user.health_unit:
                raise forms.ValidationError("Administradores locais só podem atribuir usuários à sua própria unidade.")
        return health_unit


class ProfessionalLoginForm(AuthenticationForm):
    """
    Formulário de login para profissionais de saúde (Médicos).
    Aceita CPF ou Registro Profissional.
    """
    username = forms.CharField(
        label="CPF ou Registro Profissional",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Seu CPF ou Registro Profissional'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username_input = cleaned_data.get('username')
        password = cleaned_data.get('password')
        User = get_user_model()

        if username_input and password:
            user = None
            user_obj = None

            # Tenta encontrar o usuário por CPF (USERNAME_FIELD)
            try:
                user_obj = User.objects.get(cpf=username_input) # Busca pelo CPF
            except User.DoesNotExist:
                # Se não encontrou por CPF, tenta por RP
                try:
                    user_obj = User.objects.get(professional_registration=username_input)
                except User.DoesNotExist:
                    pass

            if user_obj:
                # Autentica usando o CPF do usuário encontrado (USERNAME_FIELD)
                user = authenticate(self.request, username=user_obj.cpf, password=password)
            
            if user is None:
                raise forms.ValidationError(
                    "Credenciais inválidas. Verifique seu CPF/Registro Profissional e senha."
                )
            
            # Validar tipo de usuário para login profissional
            if user.user_type != 'professional': 
                raise forms.ValidationError(
                    "Este login é apenas para profissionais de saúde. Por favor, use a opção de login de administrador, se aplicável."
                )

            self.user_cache = user
        return cleaned_data

class AdminLoginForm(AuthenticationForm):
    """
    Formulário de login para administradores (Global e Local).
    Aceita APENAS o Cêpêéfe.
    """
    username = forms.CharField(
        label="CPF do Administrador",
        max_length=11, # CPF tem 11 dígitos
        widget=forms.TextInput(attrs={'placeholder': 'Seu CPF'})
    )

    def clean(self):
        cleaned_data = super().clean()
        cpf_input = cleaned_data.get('username') # 'username' no AuthenticationForm é o campo para o CPF aqui
        password = cleaned_data.get('password')
        User = get_user_model()

        if cpf_input and password:
            user = None
            try:
                user_obj = User.objects.get(cpf=cpf_input) # Busca pelo CPF
            except User.DoesNotExist:
                raise forms.ValidationError(
                    "Credenciais inválidas. CPF não encontrado ou senha incorreta."
                )
            
            # Autentica usando o CPF do usuário encontrado (USERNAME_FIELD)
            user = authenticate(self.request, username=user_obj.cpf, password=password)

            if user is None:
                raise forms.ValidationError(
                    "Credenciais inválidas. CPF não encontrado ou senha incorreta."
                )

            # Validar tipo de usuário para login de administrador
            if user.user_type not in ['admin_global', 'admin_local']:
                raise forms.ValidationError(
                    "Este login é apenas para administradores. Por favor, use a opção de login de profissional de saúde, se aplicável."
                )

            self.user_cache = user
        return cleaned_data
