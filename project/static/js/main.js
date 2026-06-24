document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('main-search');
    const searchArea = document.getElementById('search-area');
    const navItems = document.querySelectorAll('nav li');
    const resultsContainer = document.getElementById('results-container');
    const viewName = document.getElementById('current-view-name');
    const authModal = document.getElementById('auth-modal');
    const adminPasswordInput = document.getElementById('admin-password');
    const authError = document.getElementById('auth-error');

    loadStats('movies');

    function switchView(item, view) {
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        searchArea.style.display = view === 'dashboard' ? 'flex' : 'none';
        searchInput.value = '';
        updateView(view);
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const view = item.getAttribute('data-view');
            if (view === 'admin') {
                adminPasswordInput.value = '';
                authError.textContent = '';
                authModal.style.display = 'flex';
            } else {
                switchView(item, view);
            }
        });
    });

    document.getElementById('auth-submit').addEventListener('click', async () => {
        const password = adminPasswordInput.value;
        const res = await fetch('/api/admin/auth', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });
        if (res.ok) {
            authModal.style.display = 'none';
            const adminItem = document.querySelector('[data-view="admin"]');
            switchView(adminItem, 'admin');
        } else {
            authError.textContent = 'Incorrect password.';
        }
    });

    adminPasswordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') document.getElementById('auth-submit').click();
    });

    document.getElementById('auth-cancel').addEventListener('click', () => {
        authModal.style.display = 'none';
    });

    function triggerSearch() {
        const query = searchInput.value.trim();
        if (query.length < 2) return;
        performSearch(query);
    }

    let timeout = null;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const query = e.target.value;
        if (query.length < 2) return;
        timeout = setTimeout(() => performSearch(query), 500);
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { clearTimeout(timeout); triggerSearch(); }
    });

    document.getElementById('search-icon').addEventListener('click', () => {
        clearTimeout(timeout); triggerSearch();
    });

    function highlight(text, query) {
        if (!text) return '';
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return text.replace(new RegExp(`(${escaped})`, 'gi'), '<strong>$1</strong>');
    }

    async function performSearch(query) {
        try {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, type: 'title' })
            });
            const data = await res.json();
            viewName.textContent = `Results for "${query}"`;
            const rows = data.map((item, i) => `
                <tr>
                    <td>${i + 1}</td>
                    <td>${highlight(item.title, query)}</td>
                    <td>${item.releaseDate || ''}</td>
                    <td>${item.language || ''}</td>
                    <td><em>${highlight(item.tagline, query)}</em></td>
                </tr>
            `).join('');
            resultsContainer.innerHTML = `
                <table>
                    <thead><tr><th>#</th><th>Title</th><th>Release Date</th><th>Language</th><th>Tagline</th></tr></thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        } catch (e) {
            resultsContainer.innerHTML = '<p>Search failed.</p>';
        }
    }

    async function loadStats(type) {
        try {
            const res = await fetch(`/api/stats/${type}`);
            const data = await res.json();
            renderStats(data, type);
        } catch (e) {
            resultsContainer.innerHTML = '<p>Failed to load data.</p>';
        }
    }

    function updateView(view) {
        const views = {
            dashboard: ['Featured Movies', 'movies'],
            movies:    ['Top Movies by Revenue', 'top_movies'],
            actors:    ['Highest Grossing Actors', 'actors'],
            directors: ['Top Directors', 'directors'],
            genres:    ['Genre Counts', 'genre'],
        };
        if (view === 'admin') {
            viewName.textContent = 'Administration';
            renderAdminView();
            return;
        }
        const [label, stat] = views[view] || ['Movies', 'movies'];
        viewName.textContent = label;
        loadStats(stat);
    }

    function renderStats(data, type) {
        let header = '', rows = '';

        if (type === 'movies' || type === 'top_movies') {
            header = '<tr><th>#</th><th>Title</th><th>Popularity</th><th>Revenue</th></tr>';
            rows = data.map((item, i) => `<tr><td>${i + 1}</td><td>${item.title}</td><td>${item.popularity.toFixed(1)}</td><td>$${(item.revenue / 1e6).toFixed(1)}M</td></tr>`).join('');
        } else if (type === 'actors') {
            header = '<tr><th>#</th><th>Actor</th><th>Revenue</th></tr>';
            rows = data.map((item, i) => `<tr><td>${i + 1}</td><td>${item.name}</td><td>$${(item.revenue / 1e6).toFixed(0)}M</td></tr>`).join('');
        } else if (type === 'directors') {
            header = '<tr><th>#</th><th>Director</th><th>Avg IMDB</th></tr>';
            rows = data.map((item, i) => `<tr><td>${i + 1}</td><td>${item.name}</td><td>${item.rating.toFixed(2)}</td></tr>`).join('');
        } else if (type === 'genre') {
            header = '<tr><th>#</th><th>Genre</th><th>Count</th></tr>';
            rows = data.map((item, i) => `<tr><td>${i + 1}</td><td>${item.genre}</td><td>${item.count}</td></tr>`).join('');
        }

        resultsContainer.innerHTML = `<table><thead>${header}</thead><tbody>${rows}</tbody></table>`;
    }

    function renderAdminView() {
        resultsContainer.innerHTML = `
            <div id="admin-area">
                <p>Database operations:</p>
                <button onclick="adminAction('delete')">Delete Content</button>
                <button onclick="adminAction('repopulate')">Repopulate</button>
                <button onclick="adminAction('recreate')">Recreate Tables</button>
                <div id="admin-message"></div>
            </div>
        `;
    }

    window.adminAction = async (action) => {
        if (!confirm(`Run: ${action}?`)) return;
        try {
            const res = await fetch(`/api/admin/${action}`, { method: 'POST' });
            const data = await res.json();
            document.getElementById('admin-message').textContent = data.message;
        } catch (e) {
            document.getElementById('admin-message').textContent = 'Action failed.';
        }
    };
});
