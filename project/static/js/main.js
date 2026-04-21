document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('main-search');
    const searchPills = document.querySelectorAll('.pill');
    const navItems = document.querySelectorAll('.nav-item');
    const resultsContainer = document.getElementById('results-container');
    const viewName = document.getElementById('current-view-name');
    const loader = document.getElementById('loading-overlay');

    let currentSearchType = 'title';
    let currentView = 'dashboard';

    // Initial Load
    loadStats('movies');

    // Navigation Logic
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            const view = item.getAttribute('data-view');
            currentView = view;
            updateView(view);
        });
    });

    // Search Type Selection
    searchPills.forEach(pill => {
        pill.addEventListener('click', () => {
            searchPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentSearchType = pill.getAttribute('data-type');
        });
    });

    // Search Input Logic
    let timeout = null;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const query = e.target.value;
        if (query.length < 2) return;

        timeout = setTimeout(() => {
            performSearch(query);
        }, 500);
    });

    async function performSearch(query) {
        showLoader();
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, type: currentSearchType })
            });
            const data = await response.json();
            renderSearchResults(data);
            viewName.textContent = `Search Results: "${query}"`;
        } catch (error) {
            console.error('Search failed:', error);
            resultsContainer.innerHTML = '<p class="error">Search failed. Check your connection.</p>';
        } finally {
            hideLoader();
        }
    }

    async function loadStats(type) {
        showLoader();
        try {
            const response = await fetch(`/api/stats/${type}`);
            const data = await response.json();
            renderStats(data, type);
        } catch (error) {
            console.error('Failed to load stats:', error);
        } finally {
            hideLoader();
        }
    }

    function updateView(view) {
        switch(view) {
            case 'dashboard':
                viewName.textContent = 'Popular Now';
                loadStats('movies');
                break;
            case 'movies':
                viewName.textContent = 'Top Movies by Revenue';
                loadStats('movies');
                break;
            case 'actors':
                viewName.textContent = 'Highest Grossing Actors';
                loadStats('actors');
                break;
            case 'directors':
                viewName.textContent = 'Top Rated Directors';
                loadStats('directors');
                break;
            case 'genres':
                viewName.textContent = 'Genre Trends';
                loadStats('genre');
                break;
            case 'admin':
                viewName.textContent = 'System Administration';
                renderAdminView();
                break;
        }
    }

    function renderSearchResults(data) {
        resultsContainer.className = 'results-grid';
        resultsContainer.innerHTML = data.map(item => `
            <div class="movie-card">
                <div class="poster-placeholder">
                    <i class="fas fa-film"></i>
                    ${item.popularity ? `<div style="position:absolute; bottom:10px; right:10px; background:rgba(0,0,0,0.7); padding:5px 10px; border-radius:5px; color:var(--accent-color)">★ ${item.popularity.toFixed(1)}</div>` : ''}
                </div>
                <div class="movie-info">
                    <div class="movie-title">${item.title}</div>
                    <div class="movie-meta">
                        <span>${item.releaseDate || ''}</span>
                        <span>${item.language || ''}</span>
                    </div>
                    ${item.tagline ? `<p style="font-size:0.8rem; font-style:italic; margin-top:10px; color:var(--text-secondary)">"${item.tagline}"</p>` : ''}
                </div>
            </div>
        `).join('');
    }

    function renderStats(data, type) {
        resultsContainer.className = 'stats-container';
        let tableHeader = '';
        let tableRows = '';

        if (type === 'movies') {
            tableHeader = '<tr><th>Rank</th><th>Title</th><th>Popularity</th><th>Revenue</th></tr>';
            tableRows = data.map((item, index) => `
                <tr>
                    <td class="rank">#${index + 1}</td>
                    <td><b>${item.title}</b></td>
                    <td>★ ${item.popularity.toFixed(1)}</td>
                    <td>$${(item.revenue / 1000000).toFixed(1)}M</td>
                </tr>
            `).join('');
        } else if (type === 'actors') {
            tableHeader = '<tr><th>Rank</th><th>Actor Name</th><th>Filmography Revenue</th></tr>';
            tableRows = data.map((item, index) => `
                <tr>
                    <td class="rank">#${index + 1}</td>
                    <td><b>${item.name}</b></td>
                    <td>$${(item.revenue / 1000000).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}M</td>
                </tr>
            `).join('');
        } else if (type === 'directors') {
            tableHeader = '<tr><th>Rank</th><th>Director Name</th><th>Avg IMDB Rating</th></tr>';
            tableRows = data.map((item, index) => `
                <tr>
                    <td class="rank">#${index + 1}</td>
                    <td><b>${item.name}</b></td>
                    <td>★ ${item.rating.toFixed(2)}</td>
                </tr>
            `).join('');
        } else if (type === 'genre') {
            tableHeader = '<tr><th>Rank</th><th>Genre</th><th>Movie Count</th></tr>';
            tableRows = data.map((item, index) => `
                <tr>
                    <td class="rank">#${index + 1}</td>
                    <td><b>${item.genre}</b></td>
                    <td>${item.count}</td>
                </tr>
            `).join('');
        }

        resultsContainer.innerHTML = `
            <table>
                <thead>${tableHeader}</thead>
                <tbody>${tableRows}</tbody>
            </table>
        `;
    }

    function renderAdminView() {
        resultsContainer.className = 'stats-container';
        resultsContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 20px; max-width: 400px;">
                <p style="color: var(--text-secondary)">Administrative database operations. Use with caution.</p>
                <button class="pill" style="height: 50px; background: rgba(255,0,0,0.1); border-color: #ff4d4d; color: #ff4d4d;" onclick="adminAction('delete')">Delete Database Content</button>
                <button class="pill" style="height: 50px; background: rgba(0,255,0,0.1); border-color: #4dff4d; color: #4dff4d;" onclick="adminAction('repopulate')">Repopulate Database</button>
                <button class="pill" style="height: 50px; background: rgba(0,0,255,0.1); border-color: var(--accent-color); color: var(--accent-color);" onclick="adminAction('recreate')">Recreate Database Tables</button>
                <div id="admin-message" style="margin-top: 20px; font-weight: 500;"></div>
            </div>
        `;
    }

    window.adminAction = async (action) => {
        if (!confirm(`Are you sure you want to perform: ${action}?`)) return;
        showLoader();
        try {
            const response = await fetch(`/api/admin/${action}`, { method: 'POST' });
            const data = await response.json();
            document.getElementById('admin-message').textContent = data.message;
            document.getElementById('admin-message').style.color = data.message.includes('Error') ? '#ff4d4d' : '#4dff4d';
        } catch (error) {
            document.getElementById('admin-message').textContent = 'Action failed.';
            document.getElementById('admin-message').style.color = '#ff4d4d';
        } finally {
            hideLoader();
        }
    };

    function showLoader() { loader.style.display = 'flex'; }
    function hideLoader() { loader.style.display = 'none'; }
});
