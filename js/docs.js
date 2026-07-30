/**
 * DistaMate — Google Docs API Wrapper
 */

import Auth from './auth.js';
import { DEMO_DOC } from './demo-data.js';

const Docs = {
  BASE: 'https://docs.googleapis.com/v1',

  async getDocument(docId) {
    if (Auth.isDemoMode()) return DEMO_DOC;
    return Auth.request(`${this.BASE}/documents/${docId}`);
  },

  extractText(doc) {
    if (!doc?.body?.content) return '';
    const segments = [];
    this._extractFromContent(doc.body.content, segments);
    return segments.join('\n');
  },

  _extractFromContent(content, out) {
    for (const el of content) {
      if (el.paragraph) {
        const text = (el.paragraph.elements || [])
          .map(e => e.textRun?.content || '')
          .join('');
        if (text.trim()) out.push(text.trim());
      } else if (el.table) {
        for (const row of (el.table.tableRows || [])) {
          for (const cell of (row.tableCells || [])) {
            this._extractFromContent(cell.content || [], out);
          }
        }
      } else if (el.sectionBreak || el.tableOfContents) {
        // skip
      }
    }
  },

  getDocTitle(doc) {
    return doc?.title || 'Untitled Document';
  },

  getWordCount(text) {
    return (text.match(/\S+/g) || []).length;
  },

  // Extract doc ID from URL
  parseDocId(input) {
    const match = input.match(/\/document\/d\/([a-zA-Z0-9_-]+)/);
    return match ? match[1] : input.trim();
  },
};

export default Docs;
