/**
 * DistaMate — Documents Panel Component
 */

import Docs from '../docs.js';
import AI from '../ai.js';
import { toast, escapeHtml } from '../ui.js';
import { DEMO_DOC } from '../demo-data.js';
import Auth from '../auth.js';

let _currentDoc = null;
let _currentDocText = '';

export async function renderDocsPanel(container) {
  container.innerHTML = `
    <div class="page-header">
      <div>
        <h1 class="page-title">Documents</h1>
        <p class="page-subtitle">Extract insights and analyze Google Docs</p>
      </div>
    </div>

    <div style="max-width:700px;margin:0 auto">
      <div class="section-card" style="margin-bottom:20px">
        <div class="section-header">
          <span class="section-title">📄 Open a Document</span>
        </div>
        <div style="padding:20px">
          <div class="form-group" style="margin-bottom:16px">
            <label class="form-label">Google Doc URL or ID</label>
            <div class="form-input-group">
              <input class="form-input" id="doc-url-input" type="text"
                placeholder="https://docs.google.com/document/d/... or document ID" />
              <button class="btn btn-primary" id="open-doc-btn">Open</button>
            </div>
            <p class="form-hint">Paste a Google Docs URL or Document ID. The document must be accessible with your account.</p>
          </div>
          ${Auth.isDemoMode() ? `
          <div style="margin-top:4px">
            <button class="btn btn-secondary btn-sm" id="load-demo-doc-btn">📄 Load Demo Document</button>
          </div>` : ''}
        </div>
      </div>

      <div id="doc-analysis-area"></div>
    </div>
  `;

  document.getElementById('open-doc-btn')?.addEventListener('click', () => {
    const input = document.getElementById('doc-url-input')?.value?.trim();
    if (!input) { toast.warning('Enter a document URL or ID.'); return; }
    const docId = Docs.parseDocId(input);
    openDoc(docId);
  });

  document.getElementById('doc-url-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('open-doc-btn')?.click();
  });

  document.getElementById('load-demo-doc-btn')?.addEventListener('click', () => openDoc('demo'));
}

export async function openDoc(docId, title = null) {
  const area = document.getElementById('doc-analysis-area');
  if (!area) {
    // Navigate to docs panel first
    document.querySelector('[data-panel="docs"]')?.click();
    setTimeout(() => openDoc(docId, title), 300);
    return;
  }

  area.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Fetching document & running AI analysis...</p></div>`;

  try {
    const doc = docId === 'demo' ? DEMO_DOC : await Docs.getDocument(docId);
    _currentDoc = doc;
    _currentDocText = Docs.extractText(doc);
    const docTitle = title || Docs.getDocTitle(doc);
    const wordCount = Docs.getWordCount(_currentDocText);

    // AI Analysis
    const analysis = await AI.summarizeDocument(_currentDocText);

    area.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:10px">
        <div>
          <h2 style="font-size:18px;font-weight:700;color:var(--color-text)">${escapeHtml(docTitle)}</h2>
          <div style="font-size:12px;color:var(--color-text-muted);margin-top:2px">${wordCount.toLocaleString()} words</div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-secondary btn-sm" id="re-analyze-btn">↺ Re-analyze</button>
          ${docId !== 'demo' ? `<a href="https://docs.google.com/document/d/${docId}" target="_blank" class="btn btn-ghost btn-sm">↗ Open in Docs</a>` : ''}
        </div>
      </div>

      <!-- AI Summary -->
      <div class="ai-summary-box" style="margin-bottom:20px">
        <div class="ai-summary-title">📋 Document Summary</div>
        <div class="ai-summary-text">${escapeHtml(analysis.summary)}</div>
      </div>

      <div class="doc-view-container">
        <!-- Main insights -->
        <div>
          ${analysis.keyPoints.length > 0 ? `
          <div class="insight-card" style="margin-bottom:16px">
            <div class="insight-card-header">🔍 Key Points</div>
            <div class="insight-card-body">
              ${analysis.keyPoints.map(p => `
                <div class="insight-item">
                  <div class="insight-dot"></div>
                  <span>${escapeHtml(p)}</span>
                </div>
              `).join('')}
            </div>
          </div>` : ''}

          ${analysis.actionItems.length > 0 ? `
          <div class="insight-card" style="margin-bottom:16px">
            <div class="insight-card-header">✅ Action Items</div>
            <div class="insight-card-body">
              ${analysis.actionItems.map(a => `
                <div class="insight-item">
                  <div class="insight-dot" style="background:var(--color-warning)"></div>
                  <span>${escapeHtml(a)}</span>
                </div>
              `).join('')}
            </div>
          </div>` : ''}

          <!-- Ask about doc mini-chat -->
          <div class="section-card">
            <div class="section-header">
              <span class="section-title">💬 Ask about this document</span>
            </div>
            <div style="padding:16px">
              <div id="doc-chat-area" style="max-height:200px;overflow-y:auto;margin-bottom:12px"></div>
              <div class="form-input-group">
                <input class="form-input" id="doc-question-input" type="text"
                  placeholder="What are the deadlines? Who are the stakeholders?" />
                <button class="btn btn-primary" id="ask-doc-btn">Ask</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right sidebar -->
        <div class="doc-sidebar">
          ${analysis.keyPeople.length > 0 ? `
          <div class="insight-card">
            <div class="insight-card-header">👥 Key People</div>
            <div class="insight-card-body">
              ${analysis.keyPeople.map(p => `
                <div class="insight-item">
                  <div class="insight-dot" style="background:var(--color-primary)"></div>
                  <span>${escapeHtml(p)}</span>
                </div>
              `).join('')}
            </div>
          </div>` : ''}

          ${analysis.deadlines.length > 0 ? `
          <div class="insight-card">
            <div class="insight-card-header">📅 Deadlines</div>
            <div class="insight-card-body">
              ${analysis.deadlines.map(d => `
                <div class="insight-item">
                  <div class="insight-dot" style="background:var(--color-danger)"></div>
                  <span>${escapeHtml(d)}</span>
                </div>
              `).join('')}
            </div>
          </div>` : ''}

          <!-- Document preview snippet -->
          <div class="insight-card">
            <div class="insight-card-header">📖 Document Preview</div>
            <div class="insight-card-body">
              <div style="font-size:12px;color:var(--color-text-muted);line-height:1.7;max-height:200px;overflow:auto;font-family:var(--font-mono)">
                ${escapeHtml(_currentDocText.substring(0, 600))}${_currentDocText.length > 600 ? '...' : ''}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('re-analyze-btn')?.addEventListener('click', () => openDoc(docId, title));
    document.getElementById('ask-doc-btn')?.addEventListener('click', () => askAboutDoc());
    document.getElementById('doc-question-input')?.addEventListener('keydown', e => {
      if (e.key === 'Enter') askAboutDoc();
    });

    // Update input with the docId
    const urlInput = document.getElementById('doc-url-input');
    if (urlInput) urlInput.value = docId;

  } catch (e) {
    area.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h3>Error loading document</h3><p>${escapeHtml(e.message)}</p></div>`;
  }
}

async function askAboutDoc() {
  const input = document.getElementById('doc-question-input');
  const chatArea = document.getElementById('doc-chat-area');
  if (!input || !chatArea || !_currentDocText) return;

  const question = input.value.trim();
  if (!question) return;
  input.value = '';

  chatArea.innerHTML += `<div style="background:var(--color-primary);color:white;border-radius:12px 12px 0 12px;padding:8px 12px;font-size:12px;margin-bottom:8px;margin-left:40px">${escapeHtml(question)}</div>`;

  const answerEl = document.createElement('div');
  answerEl.style.cssText = 'background:var(--color-surface2);border:1px solid var(--color-border);border-radius:0 12px 12px 12px;padding:8px 12px;font-size:12px;margin-bottom:8px;color:var(--color-text-muted);line-height:1.6';
  answerEl.textContent = '...';
  chatArea.appendChild(answerEl);
  chatArea.scrollTop = chatArea.scrollHeight;

  try {
    const prompt = `Document content:\n${_currentDocText.substring(0, 6000)}\n\nUser question: ${question}`;
    const response = await AI._call([{ role: 'user', content: prompt }],
      'You are a document assistant. Answer questions about the provided document concisely. Base your answers strictly on the document content.');
    answerEl.textContent = response;
  } catch (e) {
    answerEl.textContent = 'Error: ' + e.message;
    answerEl.style.color = 'var(--color-danger)';
  }
  chatArea.scrollTop = chatArea.scrollHeight;
}

// Export for external access
window.docsPanel = { openDoc };
