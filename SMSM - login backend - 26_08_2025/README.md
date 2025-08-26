# SMSM Login Backend

Este projeto é um sistema de autenticação e gerenciamento de usuários baseado em Django, desenvolvido para ambientes de saúde. Ele consolida diferentes tipos de usuários (administradores globais, administradores locais e profissionais de saúde) e permite o gerenciamento centralizado de contas e permissões.

## Estrutura do Projeto

accounts/ forms.py # Formulários de autenticação e cadastro de usuários 
    models.py # Modelo customizado de usuário 
    urls.py # Rotas relacionadas a autenticação e usuários 
    views.py # Lógica das views para login, logout, cadastro e gerenciamento de usuários 

demands/ models.py # Modelo de Unidade de Saúde (HealthUnit) 

templates/ accounts/ login.html # Tela de login para profissionais e administradores 
    user_detail.html # Detalhes e edição de usuário 
    user_list.html # Listagem de usuários 

README.md

## Funcionalidades

- **Login separado para profissionais de saúde e administradores**
- **Cadastro de novos usuários** (restrito a administradores)
- **Listagem e gerenciamento de usuários** (restrito a administradores globais)
- **Vínculo de usuários a Unidades de Saúde**
- **Permissões diferenciadas por tipo de usuário**
- **Validação de CPF e Registro Profissional únicos**

## Modelos Principais

- [`accounts.models.User`](accounts/models.py): Usuário customizado com campos para CPF, registro profissional, tipo de usuário e unidade de saúde.
- [`demands.models.HealthUnit`](demands/models.py): Representa uma unidade de saúde (hospital, clínica, etc).

## Como rodar o projeto

1. Instale as dependências:
    ```sh
    pip install django
    ```
2. Realize as migrações:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```
3. Crie um superusuário:
    ```sh
    python manage.py createsuperuser
    ```
4. Inicie o servidor:
    ```sh
    python manage.py runserver
    ```

## Observações

- As pastas estão nomeadas conforme as tabelas do banco de dados.
- O HTML será removido após a migração para FastAPI.

## Licença

Este projeto é de uso interno