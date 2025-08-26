from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse # Importado para futuras respostas HTTP
from .forms import ProfessionalLoginForm, AdminLoginForm, CustomUserCreationForm
from .models import User 
from demands.models import HealthUnit 

# Decorators auxiliares para verificar o tipo de usuário
def is_global_admin(user):
    """Verifica se o usuário é um administrador global."""
    return user.is_authenticated and user.user_type == 'admin_global'

def is_local_admin(user):
    """Verifica se o usuário é um administrador local."""
    return user.is_authenticated and user.user_type == 'admin_local'

def is_doctor(user):
    """Verifica se o usuário é um médico."""
    return user.is_authenticated and user.user_type == 'doctor'

def user_can_register(user):
    """Verifica se o usuário tem permissão para cadastrar outros usuários (Admin Global ou Local)."""
    return user.is_authenticated and (user.user_type == 'admin_global' or user.user_type == 'admin_local')

def user_can_manage_all_users(user):
    """Verifica se o usuário tem permissão para listar/gerenciar todos os usuários (apenas Admin Global)."""
    return user.is_authenticated and user.user_type == 'admin_global'

def user_can_manage_user_detail(request_user, target_user):
    """Verifica se o usuário logado pode gerenciar o usuário alvo."""
    # Admin Global pode gerenciar qualquer um
    if request_user.user_type == 'admin_global':
        return True
    # Admin Local pode gerenciar usuários da sua própria unidade (incluindo ele mesmo)
    if request_user.user_type == 'admin_local' and request_user.health_unit == target_user.health_unit:
        return True
    # Um usuário pode ver/editar seu próprio perfil
    if request_user == target_user:
        return True
    return False

def login_view(request):
    """
    View para a tela de login.
    Oferece opções de login separadas para Profissionais de Saúde e Administradores.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    professional_form = ProfessionalLoginForm()
    admin_form = AdminLoginForm()

    if request.method == 'POST':
        if 'professional_login' in request.POST: 
            professional_form = ProfessionalLoginForm(request, data=request.POST)
            if professional_form.is_valid():
                user = professional_form.get_user()
                login(request, user)
                messages.success(request, f"Bem-vindo(a), {user.first_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Erro no login profissional. Verifique os campos.")
        
        elif 'admin_login' in request.POST: 
            admin_form = AdminLoginForm(request, data=request.POST)
            if admin_form.is_valid():
                user = admin_form.get_user()
                login(request, user)
                messages.success(request, f"Bem-vindo(a), {user.first_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Erro no login de administrador. Verifique os campos.")
        
        else:
            messages.error(request, "Requisição de login inválida.")

    context = {
        'professional_form': professional_form,
        'admin_form': admin_form,
    }
    return render(request, 'accounts/login.html', context)

@login_required
def logout_view(request):
    """
    View para realizar o logout do usuário.
    """
    logout(request)
    messages.info(request, "Você foi desconectado(a).")
    return redirect('login')

@login_required
@user_passes_test(user_can_register, login_url='/dashboard/') 
def register_view(request):
    """
    View para o cadastro de novos usuários.
    Administradores globais e locais podem acessar.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request_user=request.user)
        if form.is_valid():
            new_user = form.save(commit=False)
            if request.user.user_type == 'admin_local':
                new_user.health_unit = request.user.health_unit
            new_user.save()
            messages.success(request, "Novo usuário cadastrado com sucesso!")
            return redirect('register') 
        else:
            messages.error(request, "Erro ao cadastrar usuário. Verifique os campos.")
    else:
        form = CustomUserCreationForm(request_user=request.user)
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@user_passes_test(user_can_manage_all_users, login_url='/dashboard/')
def user_list_view(request):
    """
    GET: Lista todos os usuários do sistema.
    Apenas Administradores Globais podem acessar.
    """
    users = User.objects.all().order_by('first_name', 'last_name')
    context = {
        'users': users,
        'title': 'Lista de Usuários do Sistema',
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
def user_detail_view(request, user_id):
    """
    GET: Exibe detalhes de um usuário e formulário para atualização.
    PUT (via POST): Atualiza os dados de um usuário.
    DELETE (via POST): Exclui um usuário.

    Permissões:
    - Admin Global: Pode ver/editar/excluir qualquer usuário.
    - Admin Local: Pode ver/editar/excluir usuários da sua própria unidade.
    - O próprio usuário: Pode ver/editar seu próprio perfil.
    """
    target_user = get_object_or_404(User, id=user_id)

    # Verifica permissão antes de qualquer ação
    if not user_can_manage_user_detail(request.user, target_user):
        messages.error(request, "Você não tem permissão para gerenciar este usuário.")
        return redirect('dashboard')

    if request.method == 'POST':
        _method = request.POST.get('_method', '').upper() # Simula PUT/DELETE
        
        if _method == 'PUT':
            # PUT (atualização)
            form = CustomUserCreationForm(request.POST, instance=target_user, request_user=request.user)
            if form.is_valid():
                updated_user = form.save(commit=False)
                # Garante que Admin Local não possa alterar a unidade de outros usuários ou de si mesmo
                if request.user.user_type == 'admin_local' and updated_user.health_unit != request.user.health_unit:
                    messages.error(request, "Administradores locais não podem alterar a unidade de saúde de usuários.")
                else:
                    updated_user.save()
                    messages.success(request, "Usuário atualizado com sucesso!")
                    return redirect('user_detail', user_id=target_user.id)
            else:
                messages.error(request, "Erro ao atualizar usuário. Verifique os campos.")
        
        elif _method == 'DELETE':
            # DELETE (exclusão)
            if request.user == target_user:
                messages.error(request, "Você não pode excluir sua própria conta através desta interface.")
            else:
                target_user.delete()
                messages.success(request, "Usuário excluído com sucesso!")
                return redirect('user_list')
        else:
            messages.error(request, "Método de requisição POST inválido para esta ação.")
            form = CustomUserCreationForm(instance=target_user, request_user=request.user) # Recarrega o formulário se houver erro

    else: # request.method == 'GET'
        form = CustomUserCreationForm(instance=target_user, request_user=request.user)
    
    context = {
        'target_user': target_user,
        'form': form,
        'title': f"Detalhes e Gerenciamento de {target_user.get_full_name()}",
    }
    return render(request, 'accounts/user_detail.html', context)