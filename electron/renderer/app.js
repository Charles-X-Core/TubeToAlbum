let currentJobId = null;
let progressInterval = null;
let currentAnalysis = null;
let _confirmResolve = null;
let lastDownloadPath = null;

// Escape HTML to prevent XSS and template breakage
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Escape string for use in onclick attribute (JavaScript string literal)
function escapeJs(str) {
    if (!str) return '';
    return String(str)
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}

// Custom confirm modal
function showConfirm(title, msg, btnText = 'Confirmar', type = 'danger') {
    return new Promise(resolve => {
        _confirmResolve = resolve;
        document.getElementById('confirm-title').textContent = title;
        document.getElementById('confirm-msg').textContent = msg;

        const icon = document.getElementById('confirm-icon');
        const okBtn = document.getElementById('confirm-ok-btn');

        if (type === 'danger') {
            icon.className = 'w-10 h-10 rounded-xl flex items-center justify-center bg-red-500/15';
            icon.innerHTML = '<svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/></svg>';
            okBtn.className = 'modal-btn-ok danger';
        } else {
            icon.className = 'w-10 h-10 rounded-xl flex items-center justify-center bg-cyan-500/15';
            icon.innerHTML = '<svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>';
            okBtn.className = 'modal-btn-ok primary';
        }

        okBtn.textContent = btnText;
        document.getElementById('confirm-modal').classList.remove('hidden');
    });
}

function confirmOk() {
    document.getElementById('confirm-modal').classList.add('hidden');
    if (_confirmResolve) _confirmResolve(true);
}

function confirmCancel() {
    document.getElementById('confirm-modal').classList.add('hidden');
    if (_confirmResolve) _confirmResolve(false);
}

// Tab navigation
function showTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('active');
    });

    document.getElementById(`tab-${tab}`).classList.remove('hidden');
    document.getElementById(`tab-btn-${tab}`).classList.add('active');

    if (tab === 'history') loadHistory();
    if (tab === 'settings') loadSettings();
}

// Toast notification
function showToast(msg, duration = 3000) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    toastMsg.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// Window controls
function minimizeWindow() { window.api.minimizeWindow(); }
function maximizeWindow() { window.api.maximizeWindow(); }
function closeWindow() { window.api.closeWindow(); }

// Select output folder via native dialog
async function selectOutputFolder() {
    try {
        const folder = await window.api.selectFolder();
        if (folder) {
            document.getElementById('output-input').value = folder;
        }
    } catch (err) {
        console.error('Folder picker error:', err);
    }
}

// Quick path buttons
function setQuickPath(type) {
    const input = document.getElementById('output-input');
    if (type === 'music') {
        input.value = '%USERPROFILE%\\Music';
    } else if (type === 'downloads') {
        input.value = '%USERPROFILE%\\Downloads';
    } else if (type === 'desktop') {
        input.value = '%USERPROFILE%\\Desktop';
    } else if (type === 'custom') {
        selectOutputFolder();
    }
}

// Open downloaded file
function openDownloadedFile() {
    if (lastDownloadPath) {
        window.api.openFile(lastDownloadPath);
    }
}

// Open folder of downloaded file
function openDownloadedFolder() {
    if (lastDownloadPath) {
        const folder = lastDownloadPath.substring(0, lastDownloadPath.lastIndexOf('\\'));
        window.api.openFolder(folder);
    }
}

// Fetch video info
async function fetchInfo() {
    const url = document.getElementById('url-input').value.trim();
    if (!url) {
        showToast('Pega una URL de YouTube primero');
        return;
    }

    const fetchBtn = document.getElementById('fetch-btn');
    fetchBtn.disabled = true;
    fetchBtn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg><span>Buscando...</span>';

    try {
        const result = await window.api.getInfo(url);
        if (result.error) {
            showToast(result.error);
            return;
        }

        currentAnalysis = result.analysis;
        const info = result.info;

        // Show cards
        document.getElementById('preview-card').classList.remove('hidden');
        document.getElementById('options-card').classList.remove('hidden');
        document.getElementById('progress-card').classList.remove('hidden');

        // Preview
        document.getElementById('preview-title').textContent = info.title || '-';
        document.getElementById('preview-artist').textContent = `Canal: ${info.artist || '-'}`;

        const duration = info.duration || 0;
        const mins = Math.floor(duration / 60);
        const secs = Math.floor(duration % 60);
        document.getElementById('preview-duration').textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

        const badge = document.getElementById('type-badge');
        if (currentAnalysis.is_music) {
            badge.textContent = 'MUSICA';
            badge.className = 'px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-emerald-500/15 text-emerald-400 border border-emerald-500/20';
        } else {
            badge.textContent = 'OTRO CONTENIDO';
            badge.className = 'px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-red-500/15 text-red-400 border border-red-500/20';
        }

        document.getElementById('preview-reasons').textContent = currentAnalysis.reasons.join(' | ');

        if (currentAnalysis.suggested_artist) {
            document.getElementById('preview-artist').textContent = `Canal: ${currentAnalysis.suggested_artist}`;
        }

        // Thumbnail
        if (info.thumbnail) {
            document.getElementById('thumbnail').src = info.thumbnail;
        }

        // Set default format
        if (currentAnalysis.is_music) {
            document.getElementById('format-select').value = 'mp3';
            document.getElementById('output-input').value = '%USERPROFILE%\\Music';
        } else {
            document.getElementById('format-select').value = 'mp4';
            document.getElementById('output-input').value = '%USERPROFILE%\\Downloads\\TubeToAlbum';
        }

        onFormatChange();
        document.getElementById('download-btn').disabled = false;

    } catch (err) {
        showToast('Error: ' + err.message);
    } finally {
        fetchBtn.disabled = false;
        fetchBtn.innerHTML = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg><span>Obtener Info</span>';
    }
}

// Format change
function onFormatChange() {
    const fmt = document.getElementById('format-select').value;
    const qualitySelect = document.getElementById('quality-select');
    const bitrateDisplay = document.getElementById('bitrate-display');

    qualitySelect.innerHTML = '';

    if (fmt === 'mp4') {
        ['360p', '480p', '720p', '1080p', 'Mejor calidad'].forEach(q => {
            const opt = document.createElement('option');
            opt.value = q.replace('p', '').replace('Mejor calidad', 'best');
            opt.textContent = q;
            qualitySelect.appendChild(opt);
        });
        qualitySelect.value = '720';
        bitrateDisplay.textContent = '720p';
        document.getElementById('output-input').value = '%USERPROFILE%\\Downloads\\TubeToAlbum';
    } else {
        ['128', '192', '256', '320'].forEach(q => {
            const opt = document.createElement('option');
            opt.value = q;
            opt.textContent = `${q} kbps`;
            qualitySelect.appendChild(opt);
        });
        qualitySelect.value = '192';
        bitrateDisplay.textContent = '192 kbps';
        document.getElementById('output-input').value = '%USERPROFILE%\\Music';

        qualitySelect.onchange = () => {
            bitrateDisplay.textContent = qualitySelect.value + ' kbps';
        };
    }
}

// Start download
async function startDownload() {
    const url = document.getElementById('url-input').value.trim();
    if (!url || !currentAnalysis) return;

    const fmt = document.getElementById('format-select').value;
    const quality = document.getElementById('quality-select').value;
    const outputDir = document.getElementById('output-input').value;

    document.getElementById('download-btn').classList.add('hidden');
    document.getElementById('cancel-btn').classList.remove('hidden');
    document.getElementById('progress-status').textContent = 'Iniciando descarga...';
    document.getElementById('progress-bar').style.width = '0%';

    try {
        const result = await window.api.startDownload({
            url,
            format: fmt,
            quality,
            output_dir: outputDir,
            is_music: currentAnalysis.is_music,
        });

        if (result.error) {
            showToast(result.error);
            resetUI();
            return;
        }

        currentJobId = result.job_id;
        pollProgress();

    } catch (err) {
        showToast('Error: ' + err.message);
        resetUI();
    }
}

// Poll progress
function pollProgress() {
    if (!currentJobId) return;

    progressInterval = setInterval(async () => {
        try {
            const data = await window.api.getProgress(currentJobId);

            document.getElementById('progress-bar').style.width = `${data.progress}%`;
            document.getElementById('progress-status').textContent = `Descargando... ${data.progress.toFixed(1)}%`;
            document.getElementById('progress-speed').textContent = data.speed || '';
            document.getElementById('progress-eta').textContent = data.eta ? `ETA: ${data.eta}` : '';

            if (data.status === 'completed') {
                clearInterval(progressInterval);
                document.getElementById('progress-status').textContent = 'Completado!';
                document.getElementById('progress-bar').style.width = '100%';
                lastDownloadPath = data.filepath;

                // Show open folder button
                document.getElementById('open-folder-btn').classList.remove('hidden');

                showToast('Descarga completada!');
                window.api.notify('TubeToAlbum', 'Descarga completada exitosamente');
                resetUI();

                // Reload history so it shows immediately when user clicks History tab
                loadHistory();
            } else if (data.status === 'error') {
                clearInterval(progressInterval);
                showToast('Error: ' + data.error);
                resetUI();
            } else if (data.status === 'cancelled') {
                clearInterval(progressInterval);
                document.getElementById('progress-status').textContent = 'Cancelado';
                showToast('Descarga cancelada');
                resetUI();
            }
        } catch (err) {
            clearInterval(progressInterval);
            resetUI();
        }
    }, 500);
}

// Cancel download
async function cancelDownload() {
    if (currentJobId) {
        await window.api.cancelDownload(currentJobId);
    }
    clearInterval(progressInterval);
    resetUI();
}

// Reset UI
function resetUI() {
    document.getElementById('download-btn').classList.remove('hidden');
    document.getElementById('cancel-btn').classList.add('hidden');
    document.getElementById('open-folder-btn').classList.add('hidden');
    currentJobId = null;
}

// Load history
async function loadHistory() {
    const tbody = document.getElementById('history-table');
    const empty = document.getElementById('history-empty');
    const thead = document.getElementById('history-thead');
    const count = document.getElementById('history-count');

    try {
        const history = await window.api.getHistory();

        if (!Array.isArray(history)) {
            throw new Error('Respuesta invalida del servidor');
        }

        if (count) count.textContent = `${history.length} descarga${history.length !== 1 ? 's' : ''}`;

        if (history.length === 0) {
            if (tbody) tbody.innerHTML = '';
            if (thead) thead.classList.add('hidden');
            if (empty) empty.classList.remove('hidden');
            return;
        }

        if (empty) empty.classList.add('hidden');
        if (thead) thead.classList.remove('hidden');

        tbody.innerHTML = history.map((entry, i) => {
            const size = entry.size > 1048576
                ? `${(entry.size / 1048576).toFixed(1)} MB`
                : entry.size > 1024
                    ? `${(entry.size / 1024).toFixed(1)} KB`
                    : entry.size > 0 ? `${entry.size} B` : 'N/A';

            const fmtColor = entry.format === 'MP4' ? 'text-red-400' : 'text-emerald-400';
            const fmtBg = entry.format === 'MP4' ? 'bg-red-500/10' : 'bg-emerald-500/10';

            const hasFile = entry.filepath && entry.filepath.length > 0;
            const safeTitle = escapeHtml(entry.title || 'Sin titulo');
            const safeArtist = escapeHtml(entry.artist || 'Desconocido');
            const safeFormat = escapeHtml(entry.format || '?');
            const safeDate = escapeHtml(entry.date || '');
            const safeFilepathAttr = hasFile ? escapeJs(entry.filepath) : '';

            return `
                <tr class="history-row group">
                    <td class="px-5 py-4 text-sm text-white/90 truncate max-w-xs" title="${safeTitle}">${safeTitle}</td>
                    <td class="px-5 py-4 text-sm text-gray-500 truncate max-w-[150px]">${safeArtist}</td>
                    <td class="px-5 py-4 text-center">
                        <span class="inline-flex px-2.5 py-1 rounded-md text-[11px] font-bold ${fmtColor} ${fmtBg}">${safeFormat}</span>
                    </td>
                    <td class="px-5 py-4 text-sm text-center text-gray-500 font-mono">${size}</td>
                    <td class="px-5 py-4 text-xs text-gray-600 whitespace-nowrap">${safeDate}</td>
                    <td class="px-5 py-4 text-right">
                        <div class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            ${hasFile ? `
                                <button onclick="openHistoryFile('${safeFilepathAttr}')" class="history-action-btn" title="Abrir archivo">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                                </button>
                                <button onclick="openHistoryFolder('${safeFilepathAttr}')" class="history-action-btn" title="Abrir carpeta">
                                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/></svg>
                                </button>
                            ` : ''}
                            <button onclick="deleteHistory(${i})" class="history-action-btn text-red-400/60 hover:text-red-400" title="Eliminar">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        console.error('Error loading history:', err);
        if (tbody) tbody.innerHTML = '';
        if (thead) thead.classList.add('hidden');
        if (empty) {
            empty.classList.remove('hidden');
            empty.querySelector('p').textContent = 'Error al cargar historial';
        }
        if (count) count.textContent = 'Error';
    }
}

// Open file from history
function openHistoryFile(filepath) {
    if (filepath) {
        window.api.openFile(filepath);
    }
}

// Open folder from history
function openHistoryFolder(filepath) {
    if (filepath) {
        const folder = filepath.substring(0, filepath.lastIndexOf('\\') !== -1 ? filepath.lastIndexOf('\\') : filepath.lastIndexOf('/'));
        if (folder) window.api.openFolder(folder);
    }
}

// Delete history entry
async function deleteHistory(index) {
    await window.api.deleteHistoryEntry(index);
    loadHistory();
    showToast('Entrada eliminada');
}

// Clear history
async function clearHistory() {
    const ok = await showConfirm('Limpiar historial', 'Se eliminarán todas las descargas del historial. Esta acción no se puede deshacer.', 'Limpiar todo', 'danger');
    if (ok) {
        await window.api.clearHistory();
        loadHistory();
        showToast('Historial limpiado');
    }
}

// Load settings
async function loadSettings() {
    try {
        const config = await window.api.getConfig();
        document.getElementById('cfg-quality').value = config.default_quality || '192';
        document.getElementById('cfg-format').value = config.default_format || 'mp3';
        document.getElementById('cfg-music-dir').value = config.default_output_dir || '~/Music';
        document.getElementById('cfg-other-dir').value = config.non_music_output_dir || '~/Downloads/TubeToAlbum';
        document.getElementById('cfg-embed-thumb').checked = config.embed_thumbnail !== false;
        document.getElementById('cfg-embed-meta').checked = config.embed_metadata !== false;
        document.getElementById('cfg-clean-title').checked = config.metadata?.clean_title !== false;
    } catch (err) {
        console.error('Error loading settings:', err);
    }
}

// Save settings
async function saveSettings() {
    try {
        const config = {
            default_quality: document.getElementById('cfg-quality').value,
            default_format: document.getElementById('cfg-format').value,
            default_output_dir: document.getElementById('cfg-music-dir').value,
            non_music_output_dir: document.getElementById('cfg-other-dir').value,
            embed_thumbnail: document.getElementById('cfg-embed-thumb').checked,
            embed_metadata: document.getElementById('cfg-embed-meta').checked,
            metadata: {
                clean_title: document.getElementById('cfg-clean-title').checked,
            },
        };
        await window.api.saveConfig(config);
        showToast('Configuracion guardada!');
    } catch (err) {
        showToast('Error al guardar: ' + err.message);
    }
}

// Reset settings
async function resetSettings() {
    const ok = await showConfirm('Restablecer configuración', 'Se perderán todos los ajustes personalizados y volverán a los valores por defecto.', 'Restablecer', 'danger');
    if (ok) {
        document.getElementById('cfg-quality').value = '192';
        document.getElementById('cfg-format').value = 'mp3';
        document.getElementById('cfg-music-dir').value = '~/Music';
        document.getElementById('cfg-other-dir').value = '~/Downloads/TubeToAlbum';
        document.getElementById('cfg-embed-thumb').checked = true;
        document.getElementById('cfg-embed-meta').checked = true;
        document.getElementById('cfg-clean-title').checked = true;
        showToast('Configuracion restablecida');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Enter to fetch info when URL input is focused
    if (e.key === 'Enter' && document.activeElement.id === 'url-input') {
        e.preventDefault();
        fetchInfo();
    }

    // Ctrl+V to paste from clipboard and auto-fetch
    if (e.ctrlKey && e.key === 'v') {
        const urlInput = document.getElementById('url-input');
        if (document.activeElement !== urlInput) {
            navigator.clipboard.readText().then(text => {
                if (text && (text.includes('youtube.com') || text.includes('youtu.be') || text.includes('music.youtube.com'))) {
                    urlInput.value = text;
                    fetchInfo();
                }
            }).catch(() => {});
        }
    }

    // Escape to close modal
    if (e.key === 'Escape') {
        const modal = document.getElementById('confirm-modal');
        if (!modal.classList.contains('hidden')) {
            confirmCancel();
        }
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showTab('download');
});
