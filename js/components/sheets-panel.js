/**
 * DistaMate — Sheets Panel Component
 */

import Sheets from '../sheets.js';
import Drive from '../drive.js';
import AI from '../ai.js';
import Auth from '../auth.js';
import { toast, modal, escapeHtml, formatDate } from '../ui.js';

let _currentSheetId = null;
let _currentSheetName = 'Sheet';
let _sheetValues = [];
let _sheetMeta = null;
let _analysis = null;

export async function renderSheetsPanel(container) {
  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Sheets</h1>
        <p class="page-subtitle">View, analyze, and update Google Sheets</p>
      </div>
    </div>

    <div style="max-width:760px">
      <div class="section-card" style="margin-bottom:20px">
        <div class="section-header">
          <span class="section-title">📊 Open a Spreadsheet</span>
        </div>
        <div style="padding:20px">
          <div class="form-group">
            <label class="form-label">Google Sheets URL or ID</label>
            <div class="form-input-group">
              <input class="form-input" id="sheet-url-input" type="text"
                placeholder="https://docs.google.com/spreadsheets/d/..." />
              <button class="btn btn-primary" id="open-sheet-btn">Open</button>
            </div>
            <p class="form-hint">Paste a Google Sheets URL or Spreadsheet ID.</p>
          </div>
          ${Auth.isDemoMode() ? `
          <div style="margin-top:12px">
            <button class="btn btn-secondary btn-sm" id="load-demo-sheet-btn">📊 Load Demo Spreadsheet</button>
          </div>` : ''}
        </div>
      </div>
    </div>

    <div id="sheet-area"></div>
  `;

  document.getElementById('open-sheet-btn')?.addEventListener('click', () => {
    const input = document.getElementById('sheet-url-input')?.value?.trim();
    if (!input) { toast.warning('Enter a spreadsheet URL or ID.'); return; }
    const id = Sheets.parseSheetId(input);
    openSheet(id);
  });

  document.getElementById('sheet-url-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('open-sheet-btn')?.click();
  });

  document.getElementById('load-demo-sheet-btn')?.addEventListener('click', () => openSheet('demo', 'Q3 Budget Spreadsheet'));
}

export async function openSheet(sheetId, sheetName = null) {
  const area = document.getElementById('sheet-area');
  if (!area) {
    document.querySelector('[data-panel="sheets"]')?.click();
    setTimeout(() => openSheet(sheetId, sheetName), 300);
    return;
  }

  _currentSheetId = sheetId;
  area.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Loading spreadsheet...</p></div>`;

  try {
    const [meta, values] = await Promise.all([
      Sheets.getSpreadsheet(sheetId),
      Sheets.getSheetValues(sheetId),
    ]);

    _sheetMeta = meta;
    _sheetValues = values;
    _currentSheetName = sheetName || meta.properties?.title || 'Spreadsheet';
    const sheetNames = Sheets.getSheetNames(meta);
    const { headers, rows } = Sheets.parseValues(values);

    // AI analysis
    area.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Running AI analysis on your data...</p></div>`;
    _analysis = await AI.analyzeSheet(headers, rows).catch(() => null);

    renderSheetView(area, headers, rows, sheetNames, sheetId);

    const urlInput = document.getElementById('sheet-url-input');
    if (urlInput) urlInput.value = sheetId === 'demo' ? 'demo' : sheetId;
  } catch (e) {
    area.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error loading spreadsheet</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

function renderSheetView(area, headers, rows, sheetNames, sheetId) {
  area.innerHTML = `
    <div class="sheet-controls">
      <span class="sheet-name-display">📊 ${escapeHtml(_currentSheetName)}</span>
      <div style="display:flex;gap:6px;flex-wrap:wrap">
        ${sheetNames.map((n, i) => `<button class="btn btn-ghost btn-sm sheet-tab ${i===0?'active':''}" data-sheet="${escapeHtml(n)}">${escapeHtml(n)}</button>`).join('')}
      </div>
      <button class="btn btn-secondary btn-sm" id="append-row-btn">+ Add Row</button>
      ${sheetId !== 'demo' ? `<a href="https://docs.google.com/spreadsheets/d/${sheetId}" target="_blank" class="btn btn-ghost btn-sm">↗ Open</a>` : ''}
    </div>

    ${_analysis ? `
    <div class="ai-summary-box" style="margin-bottom:20px">
      <div class="ai-summary-title">🤖 AI Spreadsheet Analysis</div>
      <div class="ai-summary-text" style="margin-bottom:12px">${escapeHtml(_analysis.summary)}</div>
      ${_analysis.insights.length > 0 ? `
      <div class="ai-chips">
        ${_analysis.insights.map(ins => `<div class="ai-chip">💡 ${escapeHtml(ins)}</div>`).join('')}
      </div>` : ''}
    </div>` : ''}

    ${headers.length > 0 ? `
    <div class="table-wrapper">
      <table class="data-table" id="sheet-table">
        <thead>
          <tr>${headers.map((h, i) => `<th>${escapeHtml(h || `Col ${i+1}`)}</th>`).join('')}</tr>
        </thead>
        <tbody>
          ${rows.map((row, ri) => `
            <tr>
              ${headers.map((_, ci) => {
                const val = row[ci] !== undefined ? row[ci] : '';
                return `<td class="editable" data-row="${ri}" data-col="${ci}" data-range="${indexToA1(ri+1, ci)}" title="Click to edit">${escapeHtml(String(val))}</td>`;
              }).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
    <div style="margin-top:8px;font-size:12px;color:var(--color-text-muted)">${rows.length} rows × ${headers.length} columns · Click any cell to edit</div>
    ` : `<div class="empty-state"><div class="empty-icon">📊</div><h3>No data</h3><p>This sheet appears to be empty.</p></div>`}

    ${_analysis?.suggestedFormulas?.length > 0 ? `
    <div class="section-card" style="margin-top:20px">
      <div class="section-header"><span class="section-title">🔢 Suggested Formulas</span></div>
      <div style="padding:16px;display:flex;flex-direction:column;gap:10px">
        ${_analysis.suggestedFormulas.map(f => `
          <div style="background:var(--color-surface2);border:1px solid var(--color-border);border-radius:var(--radius-md);padding:12px">
            <div style="font-size:12px;font-weight:600;margin-bottom:4px">${escapeHtml(f.name)}</div>
            <div style="font-family:var(--font-mono);font-size:12px;color:var(--color-accent);margin-bottom:4px">${escapeHtml(f.formula)}</div>
            <div style="font-size:11px;color:var(--color-text-muted)">${escapeHtml(f.description)}</div>
          </div>
        `).join('')}
      </div>
    </div>` : ''}
  `;

  // Tab switching
  area.querySelectorAll('.sheet-tab').forEach(tab => {
    tab.addEventListener('click', async () => {
      area.querySelectorAll('.sheet-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const values = await Sheets.getSheetValues(sheetId, tab.dataset.sheet);
      _sheetValues = values;
      const { headers: h, rows: r } = Sheets.parseValues(values);
      const tbody = document.querySelector('#sheet-table tbody');
      if (tbody) {
        tbody.innerHTML = r.map((row, ri) => `
          <tr>${h.map((_, ci) => {
            const val = row[ci] !== undefined ? row[ci] : '';
            return `<td class="editable" data-row="${ri}" data-col="${ci}" data-range="${indexToA1(ri+1,ci)}" title="Click to edit">${escapeHtml(String(val))}</td>`;
          }).join('')}</tr>
        `).join('');
        wireTableEditing(area, sheetId, tab.dataset.sheet);
      }
    });
  });

  wireTableEditing(area, sheetId, sheetNames[0]);

  document.getElementById('append-row-btn')?.addEventListener('click', () => showAppendRowModal(sheetId, headers, sheetNames[0]));
}

function wireTableEditing(area, sheetId, sheetName) {
  area.querySelectorAll('td.editable').forEach(td => {
    td.addEventListener('click', () => editCell(td, sheetId, sheetName));
  });
}

async function editCell(td, sheetId, sheetName) {
  const currentVal = td.textContent;
  const range = `${sheetName}!${td.dataset.range}`;

  modal.show({
    title: '✏️ Edit Cell',
    body: `
      <div class="form-group">
        <label class="form-label">Cell ${td.dataset.range} — New Value</label>
        <input class="form-input" id="cell-value-input" type="text" value="${escapeHtml(currentVal)}" placeholder="Enter value or formula (=SUM(...))"/>
      </div>
      <p class="form-hint" style="margin-top:8px">⚠️ Changes will be written to your live Google Sheet after confirmation.</p>
    `,
    buttons: [
      { label: 'Cancel', class: 'btn-ghost' },
      { label: '✅ Update Cell', class: 'btn-primary', action: async () => {
        const newVal = document.getElementById('cell-value-input')?.value;
        if (newVal === currentVal) return;
        try {
          await Sheets.updateCell(sheetId, range, newVal);
          td.textContent = newVal;
          toast.success(`Cell updated: ${td.dataset.range} = ${newVal}`);
        } catch (e) {
          toast.error('Update failed: ' + e.message);
        }
      }}
    ]
  });

  setTimeout(() => {
    const input = document.getElementById('cell-value-input');
    input?.focus(); input?.select();
  }, 100);
}

async function showAppendRowModal(sheetId, headers, sheetName) {
  modal.show({
    title: '+ Add New Row',
    body: `
      <div style="display:flex;flex-direction:column;gap:10px">
        ${headers.map((h, i) => `
          <div class="form-group">
            <label class="form-label">${escapeHtml(h || `Column ${i+1}`)}</label>
            <input class="form-input" id="append-col-${i}" type="text" placeholder="${escapeHtml(h)}" />
          </div>
        `).join('')}
      </div>
    `,
    buttons: [
      { label: 'Cancel', class: 'btn-ghost' },
      { label: '+ Add Row', class: 'btn-primary', action: async () => {
        const values = headers.map((_, i) => document.getElementById(`append-col-${i}`)?.value || '');
        try {
          await Sheets.appendRow(sheetId, sheetName, values);
          toast.success('Row appended successfully!');
          openSheet(sheetId, _currentSheetName);
        } catch (e) {
          toast.error('Failed to append: ' + e.message);
        }
      }}
    ]
  });
}

function indexToA1(row, col) {
  let colStr = '';
  let c = col;
  do {
    colStr = String.fromCharCode(65 + (c % 26)) + colStr;
    c = Math.floor(c / 26) - 1;
  } while (c >= 0);
  return `${colStr}${row + 1}`;
}

window.sheetsPanel = { openSheet };
