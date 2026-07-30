/**
 * DistaMate — Google Drive API Wrapper
 */

import Auth from './auth.js';
import { DEMO_FILES } from './demo-data.js';

const Drive = {
  BASE: 'https://www.googleapis.com/drive/v3',
  FIELDS: 'id,name,mimeType,modifiedTime,size,parents,owners,webViewLink',

  async listFiles(folderId = 'root', pageSize = 30) {
    if (Auth.isDemoMode()) return DEMO_FILES;

    const q = `'${folderId}' in parents and trashed=false`;
    const params = new URLSearchParams({
      q,
      pageSize,
      fields: `files(${this.FIELDS})`,
      orderBy: 'modifiedTime desc',
    });
    const data = await Auth.request(`${this.BASE}/files?${params}`);
    return data.files || [];
  },

  async searchFiles(query, pageSize = 20) {
    if (Auth.isDemoMode()) {
      return DEMO_FILES.filter(f => f.name.toLowerCase().includes(query.toLowerCase()));
    }

    const q = `fullText contains '${query.replace(/'/g, "\\'")}' and trashed=false`;
    const params = new URLSearchParams({
      q, pageSize,
      fields: `files(${this.FIELDS})`,
      orderBy: 'modifiedTime desc',
    });
    const data = await Auth.request(`${this.BASE}/files?${params}`);
    return data.files || [];
  },

  async getRecentFiles(pageSize = 15) {
    if (Auth.isDemoMode()) return DEMO_FILES.slice(0, 8);

    const params = new URLSearchParams({
      pageSize,
      fields: `files(${this.FIELDS})`,
      orderBy: 'viewedByMeTime desc',
      q: 'trashed=false',
    });
    const data = await Auth.request(`${this.BASE}/files?${params}`);
    return data.files || [];
  },

  async getStorageQuota() {
    if (Auth.isDemoMode()) return { usage: 4831838208, limit: 16106127360 };
    const data = await Auth.request(`${this.BASE}/about?fields=storageQuota`);
    return data.storageQuota || {};
  },

  async createDoc(name) {
    if (Auth.isDemoMode()) throw new Error('Cannot create files in Demo mode.');
    const data = await Auth.request('https://www.googleapis.com/drive/v3/files', {
      method: 'POST',
      body: JSON.stringify({ name, mimeType: 'application/vnd.google-apps.document' })
    });
    return data;
  },

  async createSheet(name) {
    if (Auth.isDemoMode()) throw new Error('Cannot create files in Demo mode.');
    const data = await Auth.request('https://www.googleapis.com/drive/v3/files', {
      method: 'POST',
      body: JSON.stringify({ name, mimeType: 'application/vnd.google-apps.spreadsheet' })
    });
    return data;
  },

  getFileUrl(fileId) {
    return `https://drive.google.com/file/d/${fileId}/view`;
  },

  isFolder(mimeType) {
    return mimeType === 'application/vnd.google-apps.folder';
  },

  isDoc(mimeType) {
    return mimeType === 'application/vnd.google-apps.document';
  },

  isSheet(mimeType) {
    return mimeType === 'application/vnd.google-apps.spreadsheet';
  },
};

export default Drive;
