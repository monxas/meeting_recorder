const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let serverProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false, // Disable Node integration for security
            contextIsolation: true, // Enable context isolation for security
        },
    });

    // Load the frontend from the FastAPI server
    mainWindow.loadURL('http://localhost:8000');

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

function startServer() {
    // Start the FastAPI server as a subprocess
    serverProcess = spawn('uvicorn', ['app:app', '--host', '127.0.0.1', '--port', '8000', '--reload'], {
        cwd: path.join(__dirname, 'backend'), // Adjust the path to your backend directory
        shell: true,
        stdio: 'inherit',
    });

    serverProcess.on('close', (code) => {
        console.log(`FastAPI server exited with code ${code}`);
        app.quit();
    });
}

app.on('ready', () => {
    startServer();
    // Wait a few seconds to ensure the server starts before creating the window
    setTimeout(createWindow, 5000);
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});

app.on('activate', function () {
    if (mainWindow === null) createWindow();
});

app.on('before-quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});
