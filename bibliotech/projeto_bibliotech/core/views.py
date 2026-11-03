from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Livro, Categoria, Reserva
from .forms import LivroForm, ReservaAdminForm
from datetime import date, timedelta
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Q
from django.http import JsonResponse
from usuarios.models import UsuarioCustomizado


def adicionar_dias_uteis(data_inicial, dias):
    data_final = data_inicial
    while dias > 0:
        data_final += timedelta(days=1)
        if data_final.weekday() < 5:
            dias -= 1
    return data_final


def is_admin(user):
    return user.is_staff


@login_required
def home_view(request):
    if request.user.is_staff:
        total_livros = Livro.objects.count()
        total_reservas = Reserva.objects.count()
        reservas_pendentes = Reserva.objects.filter(status__in=['preparando', 'aguardando']).count()
        reservas_ativas = Reserva.objects.filter(status='ativa').count()
        reservas_atrasadas = Reserva.objects.filter(status='atrasado').count()
        total_usuarios = UsuarioCustomizado.objects.count()

        context = {
            'total_livros': total_livros,
            'total_reservas': total_reservas,
            'reservas_pendentes': reservas_pendentes,
            'reservas_ativas': reservas_ativas,
            'reservas_atrasadas': reservas_atrasadas,
            'total_usuarios': total_usuarios,
        }
        return render(request, 'core/home_adm.html', context)
    else:
        minhas_reservas = Reserva.objects.filter(usuario=request.user).exclude(status='devolvido')
        total_ativas = minhas_reservas.count()
        total_prontas = minhas_reservas.filter(status='aguardando').count()
        total_atrasadas = minhas_reservas.filter(status='atrasado').count()
        total_livros = Livro.objects.count()

        context = {
            'total_ativas': total_ativas,
            'total_prontas': total_prontas,
            'total_atrasadas': total_atrasadas,
            'total_livros': total_livros,
            'ultimas_reservas': minhas_reservas[:3],
        }
        return render(request, 'core/home_cliente.html', context)


def home_convidado_view(request):
    total_livros = Livro.objects.count()
    total_categorias = Categoria.objects.count()
    livros_destaque = Livro.objects.all()[:6]

    context = {
        'total_livros': total_livros,
        'total_categorias': total_categorias,
        'livros_destaque': livros_destaque,
    }
    return render(request, 'core/home_convidado.html', context)


def catalogo_view(request):
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()

    todas_categorias = Categoria.objects.all()
    livros_filtrados = None
    livros_por_categoria = {}
    categoria_selecionada = None

    if query:
        livros_filtrados = Livro.objects.filter(
            Q(titulo__icontains=query) |
            Q(autor__icontains=query) |
            Q(editora__icontains=query)
        ).distinct()
    elif categoria_id:
        categoria_selecionada = get_object_or_404(Categoria, id=categoria_id)
        livros_filtrados = Livro.objects.filter(categorias=categoria_selecionada)
    else:
        for categoria in todas_categorias:
            livros = Livro.objects.filter(categorias=categoria)
            if livros.exists():
                livros_por_categoria[categoria.nome] = livros

    context = {
        'todas_categorias': todas_categorias,
        'livros_por_categoria': livros_por_categoria,
        'livros_filtrados': livros_filtrados,
        'categoria_selecionada': categoria_selecionada,
        'query': query,
        'total_acervo': Livro.objects.count(),
    }
    return render(request, 'core/catalogo.html', context)


def livro_detalhe_view(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    categorias_do_livro = livro.categorias.all()
    livros_similares = Livro.objects.filter(categorias__in=categorias_do_livro).exclude(id=livro_id).distinct()[:12]
    
    reserva_do_usuario = None
    if request.user.is_authenticated:
        reserva_do_usuario = Reserva.objects.filter(
            livro=livro, 
            usuario=request.user, 
            status__in=['ativa', 'atrasado', 'preparando', 'aguardando']
        ).first()

    context = {
        'livro': livro,
        'livros_similares': livros_similares,
        'reserva_do_usuario': reserva_do_usuario, 
    }
    return render(request, 'core/livro_detalhe.html', context)


@login_required
def reservar_livro_view(request, livro_id):
    if request.user.is_staff:
        messages.error(request, 'Administradores não realizam reservas como alunos. Utilize o painel de gerenciamento.')
        return redirect('livro_detalhe', livro_id=livro_id)
        
    livro = get_object_or_404(Livro, id=livro_id)
    
    ja_reservado = Reserva.objects.filter(
        livro=livro, 
        usuario=request.user
    ).exclude(status='devolvido').exists()
    
    total_emprestimos = Reserva.objects.filter(usuario=request.user).exclude(status='devolvido').count()
    if total_emprestimos >= 3:
        messages.error(request, 'Você atingiu o limite máximo de 3 livros simultâneos.')
        return redirect('livro_detalhe', livro_id=livro_id)
    
    if request.method == 'POST':
        if ja_reservado:
            messages.warning(request, 'Você já possui uma reserva ativa deste livro.')
            return redirect('livro_detalhe', livro_id=livro_id)

        if livro.is_available:
            data_pronto = adicionar_dias_uteis(date.today(), 2)
            
            Reserva.objects.create(
                livro=livro,
                usuario=request.user,
                data_disponivel=data_pronto,
                status='preparando',
                data_devolucao=None
            )
            messages.success(request, f'Reserva de "{livro.titulo}" confirmada com sucesso! Aguarde a preparação.')
            return redirect('reservas_cliente')
        else:
            messages.error(request, 'Este livro está temporariamente indisponível (sem estoque).')
            return redirect('livro_detalhe', livro_id=livro_id)
    
    return redirect('livro_detalhe', livro_id=livro_id)


@login_required
def reservas_cliente_view(request):
    reservas = Reserva.objects.filter(usuario=request.user).exclude(status='devolvido').order_by('-data_reserva')
    historico = Reserva.objects.filter(usuario=request.user, status='devolvido').order_by('-data_devolucao_efetiva')[:5]
    
    context = {
        'reservas': reservas,
        'historico': historico,
    }
    return render(request, 'core/reservas_cliente.html', context)


@user_passes_test(is_admin)
def reservas_adm_view(request):
    status_filter = request.GET.get('status', '').strip()
    busca = request.GET.get('busca', '').strip()

    reservas = Reserva.objects.select_related('livro', 'usuario').all()

    if status_filter:
        reservas = reservas.filter(status=status_filter)

    if busca:
        reservas = reservas.filter(
            Q(livro__titulo__icontains=busca) |
            Q(usuario__first_name__icontains=busca) |
            Q(usuario__last_name__icontains=busca) |
            Q(usuario__username__icontains=busca)
        )

    reservas = reservas.annotate(
        ordem_prioridade=Case(
            When(status='atrasado', then=Value(0)),
            When(status='aguardando', then=Value(1)),
            When(status='preparando', then=Value(2)),
            When(status='ativa', then=Value(3)),
            When(status='devolvido', then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
    ).order_by('ordem_prioridade', '-id')

    context = {
        'reservas': reservas,
        'status_filter': status_filter,
        'busca': busca,
        'total_geral': Reserva.objects.count(),
        'total_preparando': Reserva.objects.filter(status='preparando').count(),
        'total_aguardando': Reserva.objects.filter(status='aguardando').count(),
        'total_ativa': Reserva.objects.filter(status='ativa').count(),
        'total_atrasado': Reserva.objects.filter(status='atrasado').count(),
        'total_devolvido': Reserva.objects.filter(status='devolvido').count(),
    }
    return render(request, 'core/reservas_adm.html', context)


@user_passes_test(is_admin)
def editar_reserva_adm_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        form = ReservaAdminForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, f'Reserva #{reserva.id} atualizada com sucesso!')
            return redirect('reservas_adm')
    else:
        form = ReservaAdminForm(instance=reserva)

    context = {
        'form': form,
        'reserva': reserva,
        'titulo_pagina': f"Editar Reserva #{reserva.id} - '{reserva.livro.titulo}'"
    }
    return render(request, 'core/editar_reserva_adm.html', context)


@user_passes_test(is_admin)
def adicionar_livro_view(request):
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES)
        if form.is_valid():
            novo_livro = form.save()
            messages.success(request, f'Livro "{novo_livro.titulo}" cadastrado com sucesso!') 
            return redirect('catalogo')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário abaixo.')
    else:
        form = LivroForm()

    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Livro'
    }
    return render(request, 'core/livro_form.html', context)


@user_passes_test(is_admin)
def editar_livro_view(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)
    
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, f'Livro "{livro.titulo}" atualizado com sucesso!')
            return redirect('livro_detalhe', livro_id=livro.id)
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário abaixo.')
    else:
        form = LivroForm(instance=livro)
        
    return render(request, 'core/livro_form.html', {
        'form': form, 
        'titulo_pagina': f'Editar "{livro.titulo}"',
        'livro': livro,
    })


@user_passes_test(is_admin)
def excluir_livro_view(request, livro_id):
    livro = get_object_or_404(Livro, id=livro_id)

    if request.method == 'POST':
        titulo_livro = livro.titulo 
        livro.delete()
        messages.success(request, f"O livro '{titulo_livro}' foi removido com sucesso.")
        return redirect('catalogo')

    return render(request, 'core/livro_confirm_delete.html', {'livro': livro})


def creditos_view(request):
    equipe = [
        {'nome': 'Arthur', 'cargo': 'Banco de Dados', 'desc': 'Modelagem e arquitetura relacional SQLite, migrações e consistência de dados.'},
        {'nome': 'Beatriz', 'cargo': 'Design UI/UX & Fluxogramas', 'desc': 'Design de telas, experiência de navegação e fluxograma de processos.'},
        {'nome': 'Sayuri', 'cargo': 'Gestão & Apoio de Projeto', 'desc': 'Auxiliar do projeto, controle de qualidade de requisitos e organização.'},
        {'nome': 'Igor Joe', 'cargo': 'Desenvolvimento Front-End', 'desc': 'Desenvolvimento de interfaces, estilização e interações de usuário.'},
        {'nome': 'Luiz', 'cargo': 'Diagramação & Casos de Uso', 'desc': 'Diagramas UML de Casos de Uso, mapeamento de regras de negócio e apoio geral.'},
        {'nome': 'Nicolas', 'cargo': 'Desenvolvimento Back-End', 'desc': 'Lógica de negócio Django, autenticação, controle de reservas e rotas.'},
        {'nome': 'Vitinho', 'cargo': 'Coleta & Levantamento de Dados', 'desc': 'Levantamento de requisitos com bibliotecários e catálogo inicial de livros.'},
    ]
    return render(request, 'core/creditos.html', {'equipe': equipe})


def buscar_livros_api(request):
    query = request.GET.get('q', '').strip()
    if query:
        livros = Livro.objects.filter(
            Q(titulo__icontains=query) | Q(autor__icontains=query)
        )[:8]
        results = []
        for livro in livros:
            results.append({
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'capa_url': livro.capa.url if livro.capa else '/static/images/open-book2.png'
            })
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})
