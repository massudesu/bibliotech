# 📚 BiblioTech - Sistema de Gestão de Biblioteca Escolar

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge)

<p align="center">
  <strong>Trabalho de Conclusão de Curso (TCC)</strong><br>
  Plataforma web completa para catalogação de acervos, reserva online sem filas e controle de empréstimos em bibliotecas escolares.
</p>

</div>

---

##  Sobre o Projeto

O **BiblioTech** nasceu da necessidade de modernizar e democratizar o acesso ao acervo bibliográfico escolar. Em muitas escolas, o controle de livros ainda é realizado por fichas de papel ou planilhas desconectadas, o que gera filas no balcão, perda de exemplares e baixa visibilidade das obras.

Com o BiblioTech, os alunos podem consultar todo o catálogo digitalmente, pesquisar por título ou autor em tempo real, verificar a disponibilidade e reservar livros com antecedência. Do lado da biblioteca, os gestores contam com um painel administrativo intuitivo para preparar pedidos, controlar prazos de devolução, localizar livros por corredor/prateleira e cadastrar novos títulos.

---

##  Principais Funcionalidades

###  Para os Alunos (Clientes)
- **Catálogo Interativo por Categorias**: Carrosséis organizados por gênero literário com capas em alta definição.
- **Busca em Tempo Real com Debounce**: Pesquisa instantânea por títulos e autores com dropdown inteligente.
- **Reserva Online sem Filas**: Reserva com 1 clique (com limite de até 3 livros simultâneos por aluno).
- **Acompanhamento de Status**: Rastreamento em tempo real do pedido (`Em Preparação`, `Aguardando Retirada no Balcão`, `Empréstimo Ativo`, `Atrasado`, `Devolvido`).
- **Perfil do Aluno**: Histórico de leituras realizadas, livros em andamento e upload de foto de perfil.
- **Alternador de Tema (Dark / Light)**: Interface com modo escuro e claro persistido no navegador.

###  Para os Bibliotecários (Administradores)
- **Painel de Controle (Dashboard)**: Métricas rápidas de acervo, empréstimos ativos, pedidos pendentes e alertas de atraso.
- **Gerenciamento de Reservas**: Atualização de status, lançamento de datas de retirada e devolução efetiva com ajuste automático de estoque.
- **CRUD Completo de Livros**: Cadastro com upload de capa, seleção múltipla de categorias, estoque e localização física (Corredor e Prateleira).
- **Gestão de Acervo**: Edição rápida e exclusão segura de exemplares obsoletos.

---

##  Arquitetura do Sistema

```
bibliotech/
├── README.md                           # Documentação oficial do projeto
├── ANTES DE ABRIR O PROJETO.md             # Guia rápido de inicialização
├ 
└── bibliotech/
    ├── requirements.txt                # Dependências Python do projeto
    └── projeto_bibliotech/
        ├── manage.py                   # Utilitário de comando Django
        ├── db.sqlite3                  # Banco de dados relacional SQLite
        ├── projeto_bibliotech/         # Configurações globais (settings, urls, wsgi)
        ├── core/                       # Módulo principal de livros e reservas
        │   ├── models.py               # Modelos Categoria, Livro e Reserva
        │   ├── views.py                # Lógica de negócio, catálogos e dashboards
        │   ├── urls.py                 # Rotas do core
        │   ├── forms.py                # Formulários de livros e reservas
        │   ├── tests.py                # Suíte de testes automatizados do core
        │   └── templates/core/         # Telas HTML do catálogo, dashboards e reservas
        ├── usuarios/                   # Módulo de autenticação e perfis
        │   ├── models.py               # Modelo customizado de usuário (UsuarioCustomizado)
        │   ├── views.py                # Login, cadastro, perfil e logout
        │   ├── forms.py                # Formulário com validação de nomes acentuados
        │   ├── tests.py                # Suíte de testes de usuários e autenticação
        │   └── templates/usuarios/     # Telas de login, cadastro e perfil
        ├── static/                     # Folhas de estilo (CSS), scripts (JS) e imagens
        └── media/                      # Arquivos de mídia enviados (capas e fotos)
```

---

##  Como Executar o Projeto Localmente

### Pré-requisitos
- **Python 3.10 ou superior** instalado na máquina ([Download oficial](https://www.python.org/))
- **Git** instalado

### Passo a Passo

1. **Clone ou navegue até o repositório:**
   ```bash
   cd g:/bibliotech
   ```

2. **Crie e ative um ambiente virtual (venv):**
   - No Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate
     ```
   - No Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instale as dependências:**
   ```bash
   pip install -r bibliotech/requirements.txt
   ```

4. **Aplique as migrações do banco de dados:**
   ```bash
   python bibliotech/projeto_bibliotech/manage.py migrate
   ```

5. **(Opcional) Crie um usuário administrador:**
   ```bash
   python bibliotech/projeto_bibliotech/manage.py createsuperuser
   ```

6. **Inicie o servidor de desenvolvimento:**
   ```bash
   python bibliotech/projeto_bibliotech/manage.py runserver
   ```

7. **Acesse no seu navegador:**
   Abra `http://127.0.0.1:8000/` para acessar a tela inicial do BiblioTech.

---


##  Equipe do Trabalho de Conclusão de Curso (TCC)

| Integrante | Atribuição no Projeto |
| :--- | :--- |
| **Arthur Pardini** | **Banco de Dados**: Modelagem relacional no SQLite, integridade referencial e migrações. |
| **Beatriz Mendes** | **Design UI/UX & Fluxogramas**: Mapeamento de telas, experiência de navegação e fluxograma de processos. |
| **Fernanda Sayuri** | **Gestão & Apoio de Projeto**: Controle de qualidade, validação de requisitos e organização. |
| **Igor Joe** | **Desenvolvimento Front-End**: Construção de interfaces, responsividade e interações com o usuário. |
| **Luiz Eduardo** | **Diagramação & Casos de Uso**: Especificação de Casos de Uso UML e suporte geral ao projeto. |
| **Nicolas Massuda** | **Desenvolvimento Back-End e Front-End**: Arquitetura Django, autenticação de usuários, regras de negócio, rotas, construção e estilização de interfaces |
| **Vitor** | **Coleta & Levantamento de Dados**: Entrevistas com equipes escolares e catálogo inicial de obras. |

---

<div align="center">
  <p>Desenvolvido com dedicação para a banca examinadora do Trabalho de Conclusão de Curso.</p>
</div>

### Recriado com o auxilio do google antigravity

