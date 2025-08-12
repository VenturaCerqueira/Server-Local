document.addEventListener('DOMContentLoaded', function () {
    const fileSystemView = document.getElementById('file-system-view');
    // Se a view não existir na página, pare o script para evitar erros
    if (!fileSystemView) {
        return;
    }

    const pastasData = JSON.parse(fileSystemView.dataset.pastas || '[]');
    const allFiles = Array.isArray(pastasData) ? pastasData : [];
    let currentFilteredFiles = [...allFiles];
    let currentLayout = localStorage.getItem('layout') || 'list';
    let currentFilters = { type: 'all', date: 'all' };

    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mainContent = document.getElementById('main-content');
    const loadingOverlay = document.getElementById('loading-overlay');
    const searchModal = document.getElementById('search-modal');
    const searchOverlay = document.getElementById('search-overlay');
    const searchToggle = document.getElementById('search-toggle');
    const searchInput = document.getElementById('search-input');
    const searchResultsList = document.getElementById('search-results-list');
    const propertiesModal = document.getElementById('propertiesModal');
    const fileListContainer = document.getElementById('file-list-container');
    const layoutToggle = document.getElementById('layout-toggle');
    
    let isSidebarCollapsed = false;

    // Lógica do Sidebar
    const updateSidebarState = () => {
        if (isSidebarCollapsed) {
            document.body.classList.add('body-collapsed');
        } else {
            document.body.classList.remove('body-collapsed');
        }
    };
    
    sidebarToggle.addEventListener('click', () => {
        isSidebarCollapsed = !isSidebarCollapsed;
        updateSidebarState();
    });

    // Lógica do Layout
    const applyLayout = (layout) => {
        const icon = layoutToggle.querySelector('i');
        if (layout === 'grid') {
            fileListContainer.classList.remove('list-group', 'list-group-flush');
            fileListContainer.classList.add('grid-view');
            icon.className = 'bi bi-list';
        } else {
            fileListContainer.classList.remove('grid-view');
            fileListContainer.classList.add('list-group', 'list-group-flush');
            icon.className = 'bi bi-grid-3x3-gap';
        }
        localStorage.setItem('layout', layout);
        renderFiles(currentFilteredFiles);
    };

    layoutToggle.addEventListener('click', () => {
        const newLayout = currentLayout === 'grid' ? 'list' : 'grid';
        currentLayout = newLayout;
        applyLayout(newLayout);
    });

    const renderFiles = (files) => {
        fileListContainer.innerHTML = ''; 
        if (files.length === 0) {
            fileListContainer.innerHTML = `
                <div class="empty-folder">
                    <i class="bi bi-box-seam"></i>
                    <p class="mb-0">Nenhum item encontrado com os filtros selecionados.</p>
                </div>
            `;
            return;
        }
        
        files.forEach(item => {
            const itemElement = document.createElement('div');
            
            const isGrid = currentLayout === 'grid';
            if (isGrid) {
                itemElement.classList.add('grid-item-card');
            } else {
                itemElement.classList.add('list-group-item', 'px-0', 'list-item');
            }

            let iconClass;
            let iconColor = 'var(--text-color)';
            if (item.is_dir) {
                iconClass = 'bi-folder-fill';
                iconColor = 'var(--primary-color)';
            } else {
                switch (item.type) {
                    case 'pdf': iconClass = 'bi-filetype-pdf'; iconColor = '#dc3545'; break;
                    case 'doc': case 'docx': case 'txt': iconClass = 'bi-filetype-doc'; iconColor = '#007bff'; break;
                    case 'jpg': case 'jpeg': case 'png': case 'gif': case 'svg': iconClass = 'bi-file-earmark-image-fill'; iconColor = '#28a745'; break;
                    case 'zip': iconClass = 'bi-file-earmark-zip-fill'; iconColor = '#17a2b8'; break;
                    default: iconClass = 'bi-file-earmark-text-fill'; iconColor = '#6c757d'; break;
                }
            }

            if (isGrid) {
                itemElement.innerHTML = `
                    <div class="grid-item-preview">
                        <a href="${item.is_dir ? '/browse/' + item.path : '#'}" class="nav-link-loader">
                            <i class="bi ${iconClass} preview-icon" style="color: ${iconColor};"></i>
                        </a>
                    </div>
                    <div class="grid-item-info">
                        <i class="bi ${iconClass} item-icon" style="color: ${iconColor};"></i>
                        <span class="grid-item-filename">${item.nome}</span>
                        <div class="dropdown grid-item-actions">
                            <button class="btn btn-sm btn-link dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="bi bi-three-dots-vertical"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li>
                                    <a class="dropdown-item" href="/download/${item.path}">
                                        <i class="bi bi-download me-2"></i>Download
                                    </a>
                                </li>
                                <li>
                                    <button class="dropdown-item" type="button" data-bs-toggle="modal" data-bs-target="#propertiesModal"
                                        data-name="${item.nome}" data-modified="${item.modified_at}" data-created="${item.created_at}" data-type="${item.is_dir ? 'Pasta' : 'Arquivo'}"
                                        data-file-count="${item.file_count}" data-folder-count="${item.folder_count}"
                                        data-size="${item.size}" data-size-bytes="${item.size_bytes}" data-file-type="${item.type}">
                                        <i class="bi bi-info-circle me-2"></i>Propriedades
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </div>
                `;
            } else {
                itemElement.innerHTML = `
                    <a href="${item.is_dir ? '/browse/' + item.path : '#'}" class="list-item-link nav-link-loader">
                        <i class="bi ${iconClass} me-3 fs-5" style="color: ${iconColor};"></i>
                        <span class="d-flex flex-column me-auto">
                            <span class="fw-bold text-primary">${item.nome}</span>
                            <small class="text-muted folder-size-placeholder">
                                ${item.is_dir ? `${item.file_count} arquivos, ${item.folder_count} pastas` : item.size}
                            </small>
                        </span>
                    </a>
                    <div class="item-actions-container dropdown">
                        <button class="btn btn-sm btn-link dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li>
                                <button class="dropdown-item" type="button">
                                    <i class="bi bi-folder-symlink me-2"></i>Mover
                                </button>
                            </li>
                            <li>
                                <a class="dropdown-item" href="/download/${item.path}">
                                    <i class="bi bi-download me-2"></i>Baixar
                                </a>
                            </li>
                            <li>
                                <button class="dropdown-item" type="button" data-bs-toggle="modal" data-bs-target="#propertiesModal"
                                    data-name="${item.nome}" data-modified="${item.modified_at}" data-created="${item.created_at}" data-type="${item.is_dir ? 'Pasta' : 'Arquivo'}"
                                    data-file-count="${item.file_count}" data-folder-count="${item.folder_count}"
                                    data-size="${item.size}" data-size-bytes="${item.size_bytes}" data-file-type="${item.type}">
                                    <i class="bi bi-info-circle me-2"></i>Propriedades
                                </button>
                            </li>
                        </ul>
                    </div>
                `;
            }
            fileListContainer.appendChild(itemElement);
        });
    };

    const filterFiles = () => {
        currentFilteredFiles = allFiles.filter(item => {
            const typeMatch = (currentFilters.type === 'all' || 
                               (currentFilters.type === 'dir' && item.is_dir) ||
                               (currentFilters.type === 'document' && (item.type === 'doc' || item.type === 'docx' || item.type === 'txt')) ||
                               (item.is_dir === false && item.type === currentFilters.type));

            if (!typeMatch) return false;

            const today = new Date();
            const dateParts = item.modified_at.split(' ')[0].split('/');
            const itemDate = new Date(`${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`);
            const diffTime = today - itemDate;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (currentFilters.date === 'all') return true;
            if (currentFilters.date === 'today' && diffDays <= 1) return true;
            if (currentFilters.date === 'week' && diffDays <= 7) return true;
            if (currentFilters.date === 'month' && diffDays <= 30) return true;

            return false;
        });
        renderFiles(currentFilteredFiles);
    };

    // Event Listeners para os filtros
    document.querySelectorAll('#filter-type .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            currentFilters.type = e.target.getAttribute('data-filter-type');
            filterFiles();
        });
    });

    document.querySelectorAll('#filter-date .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            currentFilters.date = e.target.getAttribute('data-filter-date');
            filterFiles();
        });
    });

    document.body.addEventListener('click', function(e) {
        const link = e.target.closest('.nav-link-loader');
        if (link) {
            const href = link.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                loadingOverlay.classList.add('show');
                window.location.href = href;
            }
        }
    });

    propertiesModal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const name = button.getAttribute('data-name');
        const type = button.getAttribute('data-type');
        const size = button.getAttribute('data-size');
        const sizeBytes = button.getAttribute('data-size-bytes');
        const modified = button.getAttribute('data-modified');
        const created = button.getAttribute('data-created');
        const fileCount = button.getAttribute('data-file-count');
        const folderCount = button.getAttribute('data-folder-count');
        
        document.getElementById('prop-name').textContent = name;
        document.getElementById('prop-type').textContent = type;
        document.getElementById('prop-modified').textContent = modified;
        document.getElementById('prop-created').textContent = created;
        
        const fileSizeRow = document.getElementById('file-size-row');
        const fileSizeInBytesRow = document.getElementById('file-size-bytes-row');
        const folderCountRow = document.getElementById('folder-count-row');
        
        if (type === 'Arquivo') {
            fileSizeRow.style.display = '';
            fileSizeInBytesRow.style.display = '';
            folderCountRow.style.display = 'none';
            document.getElementById('prop-size').textContent = size;
            document.getElementById('prop-size-bytes').textContent = `${sizeBytes} bytes`;
        } else {
            fileSizeRow.style.display = 'none';
            fileSizeInBytesRow.style.display = 'none';
            folderCountRow.style.display = '';
            document.getElementById('prop-counts').textContent = `${fileCount} arquivos, ${folderCount} pastas`;
        }
    });

    // Lidar com o botão de pesquisa
    const showSearchModal = () => {
        searchModal.classList.add('show');
        searchOverlay.classList.add('show');
        searchInput.focus();
    };

    const hideSearchModal = () => {
        searchModal.classList.remove('show');
        searchOverlay.classList.remove('show');
        searchInput.value = '';
        searchResultsList.innerHTML = '';
    };

    searchToggle.addEventListener('click', showSearchModal);
    searchOverlay.addEventListener('click', hideSearchModal);
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            showSearchModal();
        }
        if (e.key === 'Escape') {
            hideSearchModal();
        }
    });

    // Lidar com a pesquisa
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        const query = searchInput.value;
        if (query.length > 1) {
            searchTimeout = setTimeout(async () => {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                searchResultsList.innerHTML = '';
                if (results.length > 0) {
                    results.forEach(item => {
                        const li = document.createElement('li');
                        
                        let iconClass;
                        let iconColor = 'var(--text-color)';
                        if (item.is_dir) {
                            iconClass = 'bi-folder-fill';
                        } else {
                            const fileExtension = item.nome.split('.').pop().toLowerCase();
                            switch (fileExtension) {
                                case 'pdf': iconClass = 'bi-filetype-pdf'; iconColor = '#dc3545'; break;
                                case 'doc': case 'docx': iconClass = 'bi-filetype-doc'; iconColor = '#007bff'; break;
                                case 'txt': iconClass = 'bi-filetype-txt'; iconColor = '#6c757d'; break;
                                case 'jpg': case 'jpeg': case 'png': case 'gif': case 'svg': iconClass = 'bi-file-earmark-image-fill'; iconColor = '#28a745'; break;
                                case 'zip': iconClass = 'bi-file-earmark-zip-fill'; iconColor = '#17a2b8'; break;
                                default: iconClass = 'bi-file-earmark-text-fill'; break;
                            }
                        }

                        li.innerHTML = `
                        <a href="${item.is_dir ? '/browse/' + item.path : '/download/' + item.path}" class="search-results-item nav-link-loader">
                            <i class="bi ${iconClass} me-3 fs-5" style="color: ${iconColor};"></i>
                            <span class="d-flex flex-column me-auto">
                                <span class="fw-bold">${item.nome}</span>
                                <small class="text-muted">${item.path}</small>
                            </span>
                        </a>
                        `;
                        searchResultsList.appendChild(li);
                    });
                } else {
                    searchResultsList.innerHTML = `<li class="list-group-item text-muted p-3">Nenhum resultado encontrado.</li>`;
                }
            }, 300);
        } else {
            searchResultsList.innerHTML = '';
        }
    });

    // Lidar com o tema claro/escuro
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');
    const isDarkMode = localStorage.getItem('dark-mode') === 'true';

    const applyTheme = (isDark) => {
        if (isDark) {
            document.body.classList.add('dark-mode');
            themeIcon.className = 'bi bi-moon-fill';
        } else {
            document.body.classList.remove('dark-mode');
            themeIcon.className = 'bi bi-sun-fill';
        }
    };

    applyTheme(isDarkMode);

    themeToggle.addEventListener('click', () => {
        const newTheme = document.body.classList.toggle('dark-mode');
        localStorage.setItem('dark-mode', newTheme);
        applyTheme(newTheme);
    });

    // Renderização inicial
    applyLayout(currentLayout);
    if (allFiles && allFiles.length > 0) {
        renderFiles(allFiles);
    }
});

document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const uploadBtn = document.getElementById('upload-btn');
    const spinner = document.getElementById('upload-spinner');

    spinner.style.display = 'inline-block';
    uploadBtn.disabled = true;

    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();

        if (response.ok) {
            window.location.href = result.redirect_url;
        } else {
            alert('Erro no upload: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro na conexão com o servidor.');
    } finally {
        spinner.style.display = 'none';
        uploadBtn.disabled = false;
    }
});

document.getElementById('new-folder-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const form = e.target;
    const folderName = document.getElementById('folder-name-input').value;
    const currentPath = document.getElementById('new-folder-path-input').value;
    const createFolderBtn = document.getElementById('create-folder-btn');
    const spinner = document.getElementById('create-folder-spinner');
    
    spinner.style.display = 'inline-block';
    createFolderBtn.disabled = true;

    try {
        const response = await fetch('/create_folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                folder_name: folderName,
                current_path: currentPath
            }),
        });
        const result = await response.json();

        if (response.ok) {
            window.location.href = result.redirect_url;
        } else {
            alert('Erro ao criar pasta: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro na conexão com o servidor.');
    } finally {
        spinner.style.display = 'none';
        createFolderBtn.disabled = false;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const currentPathInput = document.getElementById('current-path-input');
    const newFolderPathInput = document.getElementById('new-folder-path-input');
    const pathSegments = window.location.pathname.split('/browse/');
    if (pathSegments.length > 1) {
        const currentPath = decodeURIComponent(pathSegments[1]);
        if(currentPathInput) currentPathInput.value = currentPath;
        if(newFolderPathInput) newFolderPathInput.value = currentPath;
    } else {
        if(currentPathInput) currentPathInput.value = '';
        if(newFolderPathInput) newFolderPathInput.value = '';
    }
});