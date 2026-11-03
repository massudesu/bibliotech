from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import UsuarioCustomizado


@admin.register(UsuarioCustomizado)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = UsuarioCustomizado

    list_display = ['username', 'first_name', 'last_name', 'email', 'telefone', 'genero', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'genero']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'telefone']

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('telefone', 'genero', 'foto_perfil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('first_name', 'last_name', 'email', 'telefone', 'genero')}),
    )
