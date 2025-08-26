from django.db import models
from django.contrib.auth.models import AbstractUser
from demands.models import HealthUnit

class User(AbstractUser):
    """
    Modelo de Usuário personalizado para o sistema de saúde, consolidando Profissionais e ADMs.
    Inclui um campo para o Registro Profissional (RP) e vínculo com a Unidade de Saúde.
    """
    USER_TYPE_CHOICES = (
        ("admin_global", "Administrador Global"),
        ("admin_local", "Administrador Local"),
        ("professional", "Médico"), 
    )

    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default="professional",
        verbose_name="Tipo de Usuário"
    )
    
    professional_registration = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="Registro Profissional (CRM, COREN, CRP, CRO e os caraio.)"
    )
        
    cpf = models.CharField(
        max_length=11,
        unique=True,
        verbose_name="CPF"
    )

    health_unit = models.ForeignKey(
        HealthUnit, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Unidade de Saúde"
    )

    USERNAME_FIELD = 'cpf' 
    REQUIRED_FIELDS = ['username', 'user_type', 'first_name', 'last_name'] 

    def __str__(self):
        return self.get_full_name() or self.cpf or self.username
