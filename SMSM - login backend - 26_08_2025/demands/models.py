from django.db import models
from django.utils.text import slugify

class HealthUnit(models.Model):
    """
    Representa uma Unidade de Saúde no sistema.
    As Unidades de Saúde podem ser hospitais, clínicas, postos de saúde, etc.
    """
    name = models.CharField(
        max_length=255, 
        verbose_name="Nome da Unidade de Saúde"
    )
    address = models.CharField(
        max_length=255, 
        verbose_name="Endereço Completo"
    )
    city = models.CharField(
        max_length=50,
        verbose_name="Cidade"
    )
    state = models.CharField(
        max_length=30,
        verbose_name="Estado"
    )
    zip_code = models.CharField(
        max_length=8,
        verbose_name="CEP"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Telefone de Contato",
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=255, 
        unique=True, 
        blank=True,
        help_text="Gerado automaticamente a partir do nome."
    )

    class Meta:
        verbose_name = "Unidade de Saúde"
        verbose_name_plural = "Unidades de Saúde"
        ordering = ['name']

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para gerar um slug a partir do nome
        antes de salvar o objeto.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
