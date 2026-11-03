/**
 * BiblioTech - Script Principal
 * Controle de tema, pesquisa instantânea com debounce, carrossel e menu responsivo
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Controle de Tema (Dark / Light) ---
    const botaoTema = document.getElementById('tema-do-botao');
    const htmlElement = document.documentElement;

    function atualizarIconeTema(tema) {
        if (!botaoTema) return;
        if (tema === 'light') {
            botaoTema.innerHTML = '<span class="theme-icon">🌙</span><span class="theme-label">Modo Escuro</span>';
            botaoTema.setAttribute('title', 'Mudar para tema escuro');
        } else {
            botaoTema.innerHTML = '<span class="theme-icon">☀️</span><span class="theme-label">Modo Claro</span>';
            botaoTema.setAttribute('title', 'Mudar para tema claro');
        }
    }

    const salvarTema = localStorage.getItem('tema-claro') || 'dark';
    htmlElement.setAttribute('tema-claro-escuro', salvarTema);
    atualizarIconeTema(salvarTema);

    if (botaoTema) {
        botaoTema.addEventListener('click', (e) => {
            e.preventDefault();
            const temaAtual = htmlElement.getAttribute('tema-claro-escuro');
            const novoTema = temaAtual === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('tema-claro-escuro', novoTema);
            localStorage.setItem('tema-claro', novoTema);
            atualizarIconeTema(novoTema);
        });
    }

    // --- Menu Mobile / Hamburger ---
    const hamburgerButton = document.querySelector('.hamburger-button');
    const hamburgerMenu = document.querySelector('.hamburger-menu');

    if (hamburgerButton && hamburgerMenu) {
        hamburgerButton.addEventListener('click', (e) => {
            e.stopPropagation();
            hamburgerMenu.classList.toggle('is-active');
            const isOpen = hamburgerMenu.classList.contains('is-active');
            hamburgerButton.setAttribute('aria-expanded', isOpen);
        });

        document.addEventListener('click', (e) => {
            if (!hamburgerMenu.contains(e.target) && !hamburgerButton.contains(e.target)) {
                hamburgerMenu.classList.remove('is-active');
            }
        });
    }

    // --- Pesquisa em tempo real com Debounce ---
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    let debounceTimer = null;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.style.display = 'none';
                searchResults.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/buscar-livros/?q=${encodeURIComponent(query)}`)
                    .then(response => {
                        if (!response.ok) throw new Error('Erro na busca');
                        return response.json();
                    })
                    .then(data => {
                        searchResults.innerHTML = '';
                        if (data.results && data.results.length > 0) {
                            searchResults.style.display = 'block';
                            data.results.forEach(livro => {
                                const item = document.createElement('a');
                                item.href = `/livro/${livro.id}/`;
                                item.classList.add('search-item');
                                item.innerHTML = `
                                    <img src="${livro.capa_url}" alt="${livro.titulo}" onerror="this.src='/static/images/open-book2.png'">
                                    <div class="search-info">
                                        <h4>${livro.titulo}</h4>
                                        <p>${livro.autor}</p>
                                    </div>
                                `;
                                searchResults.appendChild(item);
                            });
                        } else {
                            searchResults.style.display = 'block';
                            searchResults.innerHTML = `
                                <div class="search-no-results">
                                    <p>Nenhum livro encontrado para "<strong>${query}</strong>"</p>
                                </div>
                            `;
                        }
                    })
                    .catch(() => {
                        searchResults.style.display = 'none';
                    });
            }, 250);
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // --- Fechamento de Mensagens / Toasts ---
    const closeButtons = document.querySelectorAll('.message-close');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const li = this.closest('li');
            if (li) {
                li.style.opacity = '0';
                li.style.transform = 'translateY(-8px)';
                setTimeout(() => li.remove(), 250);
            }
        });
    });

    // Auto-dismiss após 6 segundos para mensagens de sucesso
    const successMessages = document.querySelectorAll('.messages li.success');
    successMessages.forEach(msg => {
        setTimeout(() => {
            if (msg.parentNode) {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-8px)';
                setTimeout(() => msg.remove(), 250);
            }
        }, 6000);
    });
});

/**
 * Função global de rolagem para os carrosséis de livros
 */
function scrollCarousel(gridId, direction) {
    const gridElement = document.getElementById(gridId);
    if (!gridElement) return;

    const scrollAmount = Math.max(gridElement.clientWidth * 0.75, 260);
    gridElement.scrollBy({
        left: scrollAmount * direction,
        behavior: 'smooth'
    });
}
