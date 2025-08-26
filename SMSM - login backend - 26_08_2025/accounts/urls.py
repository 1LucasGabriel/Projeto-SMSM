from django.urls import path
from . import views

urlpatterns = [
    # URLs de Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URLs de Cadastro (POST para criar um novo usuário)
    path('register/', views.register_view, name='register'), # POST de cadastro

    # URLs de Gerenciamento de Usuários
    path('users/', views.user_list_view, name='user_list'), # GET de todos os usuários
    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'), # GET de um usuário por ID, PUT e DELETE
]
