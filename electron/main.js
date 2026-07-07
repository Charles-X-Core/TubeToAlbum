const { app, BrowserWindow, shell, ipcMain, dialog, Notification } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let backendProcess;

const BACKEND_URL = 'http://127.0.0.1:5000';
const isDev = process.argv.includes('--dev');

function startBackend() {
    const backendPath = path.join(__dirname, '..', 'backend', 'server.py');
    backendProcess = spawn('python', [backendPath], {
        stdio: 'pipe',
        cwd: path.join(__dirname, '..'),
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.log(`Backend error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend exited with code ${code}`);
    });
}

function waitForBackend(callback, retries = 20) {
    const http = require('http');
    const req = http.get(`${BACKEND_URL}/api/config`, (res) => {
        if (res.statusCode === 200) {
            callback();
        } else {
            setTimeout(() => waitForBackend(callback, retries - 1), 500);
        }
    });

    req.on('error', () => {
        if (retries > 0) {
            setTimeout(() => waitForBackend(callback, retries - 1), 500);
        } else {
            console.error('Backend failed to start');
            app.quit();
        }
    });

    req.end();
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1100,
        height: 800,
        minWidth: 900,
        minHeight: 600,
        title: 'TubeToAlbum',
        backgroundColor: '#080c18',
        icon: path.join(__dirname, 'assets', 'icon.ico'),
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            contextIsolation: true,
            nodeIntegration: false,
        },
        frame: false,
        titleBarStyle: 'hidden',
    });

    mainWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

// IPC handlers for window controls
ipcMain.on('window-minimize', () => {
    if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
    if (mainWindow) {
        if (mainWindow.isMaximized()) {
            mainWindow.unmaximize();
        } else {
            mainWindow.maximize();
        }
    }
});

ipcMain.on('window-close', () => {
    if (mainWindow) mainWindow.close();
});

ipcMain.on('open-folder', (event, folderPath) => {
    shell.openPath(folderPath);
});

ipcMain.on('open-file', (event, filePath) => {
    shell.openPath(filePath);
});

ipcMain.handle('select-folder', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Seleccionar carpeta de destino',
    });
    if (result.canceled) return null;
    return result.filePaths[0];
});

ipcMain.on('notify', (event, { title, body }) => {
    if (Notification.isSupported()) {
        new Notification({ title, body }).show();
    }
});

app.whenReady().then(() => {
    startBackend();

    waitForBackend(() => {
        createWindow();
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
});
