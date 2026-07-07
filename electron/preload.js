const { contextBridge, ipcRenderer } = require('electron');

const API_BASE = 'http://127.0.0.1:5000';

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    });
    return response.json();
}

contextBridge.exposeInMainWorld('api', {
    getInfo: (url) => apiCall('/api/info', {
        method: 'POST',
        body: JSON.stringify({ url }),
    }),

    startDownload: (data) => apiCall('/api/download', {
        method: 'POST',
        body: JSON.stringify(data),
    }),

    getProgress: (jobId) => apiCall(`/api/progress/${jobId}`),

    cancelDownload: (jobId) => apiCall(`/api/cancel/${jobId}`, {
        method: 'POST',
    }),

    getHistory: () => apiCall('/api/history'),

    clearHistory: () => apiCall('/api/history', { method: 'DELETE' }),

    deleteHistoryEntry: (index) => apiCall(`/api/history/${index}`, {
        method: 'DELETE',
    }),

    getConfig: () => apiCall('/api/config'),

    saveConfig: (config) => apiCall('/api/config', {
        method: 'POST',
        body: JSON.stringify(config),
    }),

    minimizeWindow: () => ipcRenderer.send('window-minimize'),
    maximizeWindow: () => ipcRenderer.send('window-maximize'),
    closeWindow: () => ipcRenderer.send('window-close'),
    openFolder: (path) => ipcRenderer.send('open-folder', path),
    openFile: (path) => ipcRenderer.send('open-file', path),
    selectFolder: () => ipcRenderer.invoke('select-folder'),
    notify: (title, body) => ipcRenderer.send('notify', { title, body }),
});
