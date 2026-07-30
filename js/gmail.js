/**
 * DistaMate — Gmail API Wrapper
 */

import Auth from './auth.js';
import { DEMO_EMAILS } from './demo-data.js';

const Gmail = {
  BASE: 'https://gmail.googleapis.com/gmail/v1/users/me',

  async listMessages(maxResults = 20, query = '') {
    if (Auth.isDemoMode()) return DEMO_EMAILS;

    const params = new URLSearchParams({ maxResults, ...(query ? { q: query } : {}) });
    const data = await Auth.request(`${this.BASE}/messages?${params}`);
    if (!data.messages) return [];

    const messages = await Promise.allSettled(
      data.messages.slice(0, maxResults).map(m => this.getMessage(m.id))
    );
    return messages
      .filter(r => r.status === 'fulfilled')
      .map(r => r.value);
  },

  async getMessage(id) {
    const data = await Auth.request(`${this.BASE}/messages/${id}?format=full`);
    return this._parseMessage(data);
  },

  async getThread(threadId) {
    if (Auth.isDemoMode()) {
      const email = DEMO_EMAILS.find(e => e.threadId === threadId);
      return email ? [email] : [DEMO_EMAILS[0]];
    }
    const data = await Auth.request(`${this.BASE}/threads/${threadId}?format=full`);
    return (data.messages || []).map(m => this._parseMessage(m));
  },

  async sendMessage({ to, subject, body, threadId, inReplyTo, references }) {
    if (Auth.isDemoMode()) throw new Error('Cannot send email in Demo mode.');

    const rawEmail = [
      `To: ${to}`,
      `Subject: ${subject}`,
      inReplyTo ? `In-Reply-To: ${inReplyTo}` : '',
      references ? `References: ${references}` : '',
      threadId ? `Thread-Id: ${threadId}` : '',
      'Content-Type: text/plain; charset=utf-8',
      'MIME-Version: 1.0',
      '',
      body,
    ].filter(Boolean).join('\r\n');

    const encodedEmail = btoa(unescape(encodeURIComponent(rawEmail)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

    return Auth.request(`${this.BASE}/messages/send`, {
      method: 'POST',
      body: JSON.stringify({
        raw: encodedEmail,
        ...(threadId ? { threadId } : {}),
      })
    });
  },

  async createDraft({ to, subject, body, threadId }) {
    if (Auth.isDemoMode()) throw new Error('Cannot create draft in Demo mode.');

    const rawEmail = [
      `To: ${to}`, `Subject: ${subject}`,
      'Content-Type: text/plain; charset=utf-8',
      'MIME-Version: 1.0', '', body
    ].join('\r\n');

    const encoded = btoa(unescape(encodeURIComponent(rawEmail)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

    return Auth.request(`${this.BASE}/drafts`, {
      method: 'POST',
      body: JSON.stringify({ message: { raw: encoded, ...(threadId ? { threadId } : {}) } })
    });
  },

  _parseMessage(data) {
    const headers = {};
    (data.payload?.headers || []).forEach(h => { headers[h.name.toLowerCase()] = h.value; });

    const body = this._extractBody(data.payload);
    const sender = headers.from || '';
    const senderName = sender.replace(/<.*>/, '').trim().replace(/"/g, '') || sender.split('@')[0];
    const senderEmail = (sender.match(/<(.+?)>/) || [])[1] || sender;

    return {
      id: data.id,
      threadId: data.threadId,
      subject: headers.subject || '(no subject)',
      from: senderName || senderEmail,
      fromEmail: senderEmail,
      to: headers.to || '',
      date: headers.date || '',
      snippet: data.snippet || '',
      body: body,
      labelIds: data.labelIds || [],
      isUnread: (data.labelIds || []).includes('UNREAD'),
      internalDate: data.internalDate,
    };
  },

  _extractBody(payload) {
    if (!payload) return '';
    if (payload.body?.data) return this._decode(payload.body.data);

    const parts = payload.parts || [];
    const plain = parts.find(p => p.mimeType === 'text/plain');
    if (plain?.body?.data) return this._decode(plain.body.data);

    const html = parts.find(p => p.mimeType === 'text/html');
    if (html?.body?.data) {
      const raw = this._decode(html.body.data);
      return raw.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    }

    for (const part of parts) {
      const nested = this._extractBody(part);
      if (nested) return nested;
    }
    return '';
  },

  _decode(base64url) {
    try {
      const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
      return decodeURIComponent(escape(atob(base64)));
    } catch { return ''; }
  }
};

export default Gmail;
