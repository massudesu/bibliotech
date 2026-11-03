from django.db import models
from django.conf import settings 
from datetime import date, timedelta


class Categoria(models.Model):
    nome = models.CharField(max_length=100) 

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editora = models.CharField(max_length=100)
    categorias = models.ManyToManyField(Categoria, blank=True)
    capa = models.ImageField(upload_to='capas_livros/', default='capas_livros/default.png')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    data_limite_dias = models.IntegerField(default=15)
    quantidade = models.PositiveIntegerField(default=1)
    corredor = models.CharField(max_length=50, blank=True, null=True)
    prateleira = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def is_available(self):
        return self.quantidade > 0


class Reserva(models.Model):
    STATUS_CHOICES = [
        ('preparando', 'Em Preparação'),
        ('aguardando', 'Aguardando Retirada'),
        ('ativa', 'Retirado / Empréstimo Ativo'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
    ]

    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservas')
    data_reserva = models.DateField(auto_now_add=True) 
    data_disponivel = models.DateField(null=True, blank=True)
    data_emprestimo = models.DateField(null=True, blank=True)
    data_devolucao = models.DateField(null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparando')
    data_devolucao_efetiva = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_reserva']

    def __str__(self):
        return f"{self.livro.titulo} - {self.usuario.username} ({self.get_status_display()})"

    @property
    def esta_pronto_para_retirada(self):
        if self.status == 'preparando' and self.data_disponivel and date.today() >= self.data_disponivel:
            return True
        return self.status == 'aguardando'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            if self.livro.quantidade > 0:
                self.livro.quantidade -= 1
                self.livro.save(update_fields=['quantidade'])

        if not is_new and self.pk:
            try:
                old_instance = Reserva.objects.get(pk=self.pk)
                if self.status == 'devolvido' and old_instance.status != 'devolvido':
                    today = date.today()
                    self.data_devolucao_efetiva = today
                    if not self.data_devolucao:
                        self.data_devolucao = today
                    if not self.data_emprestimo:
                        self.data_emprestimo = today
                    self.livro.quantidade += 1
                    self.livro.save(update_fields=['quantidade'])
            except Reserva.DoesNotExist:
                pass

        if self.status in ['ativa', 'atrasado'] and not self.data_emprestimo:
            self.data_emprestimo = date.today()
            self.data_devolucao = date.today() + timedelta(days=self.livro.data_limite_dias)

        super().save(*args, **kwargs)
