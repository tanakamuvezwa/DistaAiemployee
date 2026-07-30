/**
 * DistaMate — Drive Panel Component
 */

import Drive from '../drive.js';
import AI from '../ai.js';
import { toast, modal, formatDate, formatBytes, getFileIcon, getFileIconBg, escapeHtml, debounce } from '../ui.js';

let _folderStack = [{ id: 'root', name: 'My Drive' }];
let _currentFiles = [];

export async function renderDrivePanel(container) {
  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Drive</h1>
        <p class="page-subtitle">Browse and manage your Google Drive files</p>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn btn-secondary btn-sm" id="new-doc-btn">📝 New Doc</button>
        <button class="btn btn-accent btn-sm" id="new-sheet-btn">📊 New Sheet</button>
      </div>
    </div>

    <div class="drive-toolbar">
      <div class="search-input-wrapper">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input class="search-input" id="drive-search" type="text" placeholder="Search files (AI-powered)..." />
      </div>
      <button class="btn btn-secondary btn-sm" id="drive-search-btn">Search</button>
    </div>

    <div class="breadcrumb" id="drive-breadcrumb"></div>

    <div id="drive-files-area">
      <div class="loading-state"><div class="spinner"></div><p>Loading Drive...</p></div>
    </div>
  `;

  document.getElementById('new-doc-btn')?.addEventListener('click', () => createFile('doc'));
  document.getElementById('new-sheet-btn')?.addEventListener('click', () => createFile('sheet'));

  const searchInput = document.getElementById('drive-search');
  const searchBtn = document.getElementById('drive-search-btn');

  searchBtn?.addEventListener('click', () => searchDrive(searchInput?.value?.trim()));
  searchInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchDrive(searchInput.value.trim());
  });

  await loadFolder('root');
}

async function loadFolder(folderId, folderName = null) {
  if (folderName && folderId !== 'root') {
    const existing = _folderStack.find(f => f.id === folderId);
    if (!existing) _folderStack.push({ id: folderId, name: folderName });
  } else if (folderId === 'root') {
    _folderStack = [{ id: 'root', name: 'My Drive' }];
  }

  renderBreadcrumb();

  const area = document.getElementById('drive-files-area');
  if (area) area.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading folder...</p></div>`;

  try {
    _currentFiles = await Drive.listFiles(folderId);
    renderFiles(_currentFiles, area);
  } catch (e) {
    if (area) area.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

async function searchDrive(query) {
  if (!query) { loadFolder('root'); return; }

  const area = document.getElementById('drive-files-area');
  if (area) area.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Searching with AI query reformulation...</p></div>`;

  try {
    // AI reformulates the search query
    const aiQuery = await AI.reformulateSearchQuery(query).catch(() => query);
    const files = await Drive.searchFiles(aiQuery);
    _currentFiles = files;

    // Reset breadcrumb for search
    document.getElementById('drive-breadcrumb').innerHTML = `
      <span class="breadcrumb-item" onclick="window.drivePanel.goRoot()">My Drive</span>
      <span class="breadcrumb-sep">›</span>
      <span class="breadcrumb-item current">Search: "${escapeHtml(query)}"</span>
    `;

    renderFiles(files, area, `Search results for "${query}"`);
  } catch (e) {
    if (area) area.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Search failed</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

function renderFiles(files, area, title = null) {
  if (!area) return;

  if (files.length === 0) {
    area.innerHTML = `<div class="empty-state"><div class="empty-icon">📂</div><h3>Empty folder</h3><p>No files found here.</p></div>`;
    return;
  }

  area.innerHTML = `
    ${title ? `<h3 style="font-size:13px;color:var(--color-text-muted);margin-bottom:14px">${escapeHtml(title)} (${files.length} results)</h3>` : ''}
    <div class="files-grid">
      ${files.map((f, i) => renderFileCard(f, i)).join('')}
    </div>
  `;

  area.querySelectorAll('.file-card').forEach((el, i) => {
    el.addEventListener('click', () => handleFileClick(files[i]));
    el.querySelector('.file-open-btn')?.addEventListener('click', (e) => {
      e.stopPropagation();
      if (files[i].webViewLink && files[i].webViewLink !== '#') window.open(files[i].webViewLink, '_blank');
    });
    el.querySelector('.file-summarize-btn')?.addEventListener('click', async (e) => {
      e.stopPropagation();
      await summarizeFile(files[i]);
    });
  });
}

function renderFileCard(file, index) {
  const icon = getFileIcon(file.mimeType, file.name);
  const bg = getFileIconBg(file.mimeType);
  const isFolder = Drive.isFolder(file.mimeType);
  const isDoc = Drive.isDoc(file.mimeType);
  const isSheet = Drive.isSheet(file.mimeType);

  return `
    <div class="file-card" style="animation:fadeSlideUp ${0.1 + index*0.03}s both">
      <div class="file-icon-area" style="background:${bg}">${icon}</div>
      <div class="file-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</div>
      <div class="file-meta">${formatDate(file.modifiedTime)}${file.size ? ' · ' + formatBytes(parseInt(file.size)) : ''}</div>
      <div class="file-actions">
        ${!isFolder ? `<button class="btn btn-ghost btn-sm file-open-btn" title="Open in Drive">↗</button>` : ''}
        ${isDoc || isSheet ? `<button class="btn btn-secondary btn-sm file-summarize-btn" title="AI Summarize">✨</button>` : ''}
      </div>
    </div>
  `;
}

function handleFileClick(file) {
  if (Drive.isFolder(file.mimeType)) {
    loadFolder(file.id, file.name);
  } else if (Drive.isDoc(file.mimeType)) {
    document.querySelector('[data-panel="docs"]')?.click();
    setTimeout(() => window.docsPanel?.openDoc?.(file.id, file.name), 200);
  } else if (Drive.isSheet(file.mimeType)) {
    document.querySelector('[data-panel="sheets"]')?.click();
    setTimeout(() => window.sheetsPanel?.openSheet?.(file.id, file.name), 200);
  } else if (file.webViewLink && file.webViewLink !== '#') {
    window.open(file.webViewLink, '_blank');
  }
}

async function summarizeFile(file) {
  toast.info('Summarizing document...');
  try {
    if (Drive.isDoc(file.mimeType)) {
      document.querySelector('[data-panel="docs"]')?.click();
      setTimeout(() => window.docsPanel?.openDoc?.(file.id, file.name), 200);
    } else if (Drive.isSheet(file.mimeType)) {
      document.querySelector('[data-panel="sheets"]')?.click();
      setTimeout(() => window.sheetsPanel?.openSheet?.(file.id, file.name), 200);
    }
  } catch (e) {
    toast.error(e.message);
  }
}

async function createFile(type) {
  const label = type === 'doc' ? 'document' : 'spreadsheet';
  const defaultName = type === 'doc' ? 'New Document' : 'New Spreadsheet';

  modal.show({
    title: `Create New ${type === 'doc' ? 'Document' : 'Spreadsheet'}`,
    body: `
      <div class="form-group">
        <label class="form-label">File Name</label>
        <input class="form-input" id="new-file-name" type="text" value="${defaultName}" placeholder="Enter file name" />
      </div>
    `,
    buttons: [
      { label: 'Cancel', class: 'btn-ghost' },
      { label: `Create ${type === 'doc' ? '📝' : '📊'}`, class: 'btn-primary', action: async () => {
        const name = document.getElementById('new-file-name')?.value?.trim() || defaultName;
        try {
          const file = type === 'doc' ? await Drive.createDoc(name) : await Drive.createSheet(name);
          toast.success(`${label} "${name}" created!`);
          if (file.webViewLink) window.open(file.webViewLink, '_blank');
          await loadFolder(_folderStack[_folderStack.length - 1].id);
        } catch (e) {
          toast.error('Create failed: ' + e.message);
        }
      }}
    ]
  });

  setTimeout(() => {
    const input = document.getElementById('new-file-name');
    input?.focus(); input?.select();
  }, 100);
}

function renderBreadcrumb() {
  const bc = document.getElementById('drive-breadcrumb');
  if (!bc) return;
  bc.innerHTML = _folderStack.map((f, i) => {
    const isCurrent = i === _folderStack.length - 1;
    return `
      ${i > 0 ? '<span class="breadcrumb-sep">›</span>' : ''}
      <span class="breadcrumb-item ${isCurrent ? 'current' : ''}" data-idx="${i}">${escapeHtml(f.name)}</span>
    `;
  }).join('');

  bc.querySelectorAll('.breadcrumb-item:not(.current)').forEach(el => {
    el.addEventListener('click', () => {
      const idx = parseInt(el.dataset.idx);
      _folderStack = _folderStack.slice(0, idx + 1);
      loadFolder(_folderStack[idx].id);
    });
  });
}

window.drivePanel = { goRoot: () => loadFolder('root') };
