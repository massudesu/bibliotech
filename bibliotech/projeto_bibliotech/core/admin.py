from django.contrib import admin
from .models import Categoria, Livro, Reserva


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'editora', 'quantidade', 'corredor', 'prateleira', 'rating')
    list_filter = ('categorias',)
    search_fields = ('titulo', 'autor', 'editora')
    filter_horizontal = ('categorias',)
    ordering = ('titulo',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'livro', 'usuario', 'status', 'data_reserva', 'data_emprestimo', 'data_devolucao')
    list_filter = ('status', 'data_reserva', 'data_devolucao')
    search_fields = ('livro__titulo', 'usuario__username', 'usuario__first_name', 'usuario__last_name')
    date_hierarchy = 'data_reserva'
    ordering = ('-data_reserva',)
