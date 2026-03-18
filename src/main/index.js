import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import icon from '../../resources/icon.png?asset'
import { spawn } from 'child_process'
import { writeFile, unlink } from 'fs/promises'
import { tmpdir } from 'os'
import { existsSync } from 'fs'
import { checkAuthentication, authenticateWithBrowser, getAuthUrl } from './googleAuth'

let mainWindowInstance = null

function createWindow() {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindowInstance = mainWindow

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // IPC test
  ipcMain.on('ping', () => console.log('pong'))

  // Google Calendar Authentication IPC handlers
  ipcMain.handle('check-google-auth', async () => {
    try {
      return await checkAuthentication()
    } catch (error) {
      console.error('Error checking Google auth:', error)
      return { authenticated: false, needsAuth: true, error: error.message }
    }
  })

  ipcMain.handle('authenticate-google', async () => {
    try {
      if (!mainWindowInstance) {
        throw new Error('Main window not available')
      }
      const result = await authenticateWithBrowser(mainWindowInstance)
      return result
    } catch (error) {
      console.error('Error authenticating with Google:', error)
      // Provide more helpful error message
      let errorMessage = error.message
      if (error.message.includes('credentials.json not found')) {
        errorMessage =
          'Google Calendar credentials not found.\n\n' +
          'Please download credentials.json from Google Cloud Console and place it in:\n' +
          'src/python/credentials.json\n\n' +
          'See the terminal for detailed instructions.'
      }
      return { success: false, error: errorMessage }
    }
  })

  ipcMain.handle('get-google-auth-url', async () => {
    try {
      const url = await getAuthUrl()
      return { success: true, url }
    } catch (error) {
      console.error('Error getting auth URL:', error)
      return { success: false, error: error.message }
    }
  })

  // Helper function to find Python executable
  function findPythonExecutable() {
    // First, try to use virtual environment Python if it exists
    if (is.dev) {
      const venvPython = join(__dirname, '../../venv/bin/python')
      const venvPython3 = join(__dirname, '../../venv/bin/python3')
      if (existsSync(venvPython)) {
        return venvPython
      }
      if (existsSync(venvPython3)) {
        return venvPython3
      }
    } else {
      // In production, check for venv in app resources
      const appPath = app.getAppPath()
      const venvPaths = [
        join(appPath, '../app.asar.unpacked/venv/bin/python'),
        join(appPath, '../app.asar.unpacked/venv/bin/python3'),
        join(appPath, 'venv/bin/python'),
        join(appPath, 'venv/bin/python3')
      ]
      for (const venvPath of venvPaths) {
        if (existsSync(venvPath)) {
          return venvPath
        }
      }
    }

    // Fallback to system Python
    const pythonCommands = ['python3', 'python']
    for (const cmd of pythonCommands) {
      try {
        // Try to find python in PATH
        const { execSync } = require('child_process')
        execSync(`which ${cmd}`, { stdio: 'ignore' })
        return cmd
      } catch {
        continue
      }
    }
    // Final fallback to python (Windows default)
    return 'python'
  }

  // Helper function to get Python directory path (works in both dev and production)
  function getPythonDirectory() {
    // Try multiple possible locations in order of preference
    const possiblePaths = []

    if (is.dev) {
      // In development, try __dirname-based path first
      possiblePaths.push(join(__dirname, '../../src/python'))
      // Also try app.getAppPath() in case it points to project root
      possiblePaths.push(join(app.getAppPath(), 'src/python'))
    } else {
      // In production, Python files are unpacked from asar
      const appPath = app.getAppPath()
      possiblePaths.push(join(appPath, '../app.asar.unpacked/src/python'))
      possiblePaths.push(join(appPath, '../resources/src/python'))
      possiblePaths.push(join(appPath, 'src/python'))
      possiblePaths.push(join(appPath, 'python'))
    }

    // Try each path and return the first one that exists
    for (const path of possiblePaths) {
      if (existsSync(path)) {
        return path
      }
    }

    // If none exist, return the first one (will show in error message)
    return possiblePaths[0]
  }

  // IPC handler for PDF parsing
  ipcMain.handle('parse-pdf', async (event, fileBuffer) => {
    const pythonCmd = findPythonExecutable()
    const pythonDir = getPythonDirectory()
    const pythonScriptPath = join(pythonDir, 'pdf_extractor.py')

    // Log the path for debugging
    console.log('=== PDF Parser Debug Info ===')
    console.log('Is dev mode:', is.dev)
    console.log('__dirname:', __dirname)
    console.log('Python directory:', pythonDir)
    console.log('Looking for PDF extractor at:', pythonScriptPath)
    console.log('File exists:', existsSync(pythonScriptPath))
    console.log('Python command:', pythonCmd)
    console.log('============================')

    // Verify Python script exists
    if (!existsSync(pythonScriptPath)) {
      return {
        error: 'PDF extractor script not found',
        details: `Expected path: ${pythonScriptPath}`
      }
    }

    // Create temporary file for PDF
    const tempDir = tmpdir()
    const tempFilePath = join(tempDir, `pdf_${Date.now()}.pdf`)

    try {
      // Write file buffer to temp location
      await writeFile(tempFilePath, Buffer.from(fileBuffer))

      return new Promise((resolve, reject) => {
        // Spawn Python process
        const pythonProcess = spawn(pythonCmd, [pythonScriptPath, tempFilePath], {
          cwd: pythonDir,
          stdio: ['ignore', 'pipe', 'pipe']
        })

        let stdout = ''
        let stderr = ''

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString()
        })

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString()
        })

        pythonProcess.on('close', async (code) => {
          // Clean up temp file
          try {
            await unlink(tempFilePath)
          } catch (err) {
            console.error('Error deleting temp file:', err)
          }

          if (code !== 0) {
            // Parse stderr to provide better error messages
            let errorMessage = `Python process exited with code ${code}`
            let errorDetails = stderr

            // Check for common Python import errors
            if (stderr.includes('ImportError') || stderr.includes('ModuleNotFoundError')) {
              if (stderr.includes('cv2') || stderr.includes('opencv')) {
                errorMessage = 'OpenCV (cv2) import error - missing or incompatible dependencies'
                errorDetails =
                  'The OpenCV library cannot be loaded. This is usually due to missing system dependencies (like protobuf). Try running: brew reinstall opencv protobuf'
              } else if (stderr.includes('pytesseract')) {
                errorMessage = 'Tesseract OCR not found'
                errorDetails =
                  'Tesseract OCR is required but not installed. Install it with: brew install tesseract'
              } else {
                errorMessage = 'Python module import error'
              }
            } else if (stderr.includes('Library not loaded')) {
              errorMessage = 'Missing system library dependency'
              errorDetails =
                'A required system library is missing or has a version mismatch. Check the error details below.'
            }

            reject({
              error: errorMessage,
              details: errorDetails,
              stderr: stderr,
              stdout: stdout
            })
            return
          }

          try {
            // Parse JSON from stdout
            const assignments = JSON.parse(stdout.trim())
            resolve(assignments)
          } catch (parseError) {
            reject({ error: 'Failed to parse Python output', details: stdout, stderr })
          }
        })

        pythonProcess.on('error', async (err) => {
          // Clean up temp file on error
          try {
            await unlink(tempFilePath)
          } catch (unlinkError) {
            // Ignore unlink errors
            console.error('Error deleting temp file:', unlinkError)
          }
          reject({ error: `Failed to spawn Python process: ${err.message}` })
        })
      })
    } catch (error) {
      // Clean up temp file on error
      try {
        await unlink(tempFilePath)
      } catch (unlinkError) {
        // Ignore unlink errors
        console.error('Error deleting temp file:', unlinkError)
      }
      return { error: `Failed to process PDF: ${error.message}` }
    }
  })

  // IPC handler for adding assignments to calendar
  ipcMain.handle('add-to-calendar', async (event, assignments) => {
    const pythonCmd = findPythonExecutable()
    const pythonDir = getPythonDirectory()
    const pythonScriptPath = join(pythonDir, 'add_to_calendar.py')

    // Log the path for debugging
    console.log('Looking for calendar script at:', pythonScriptPath)
    console.log('Python directory:', pythonDir)
    console.log('File exists:', existsSync(pythonScriptPath))

    // Verify Python script exists
    if (!existsSync(pythonScriptPath)) {
      return {
        success: false,
        error: 'Calendar script not found',
        details: `Expected path: ${pythonScriptPath}`
      }
    }

    if (!Array.isArray(assignments) || assignments.length === 0) {
      return { success: false, error: 'No assignments provided' }
    }

    try {
      return new Promise((resolve, reject) => {
        // Spawn Python process
        const pythonProcess = spawn(pythonCmd, [pythonScriptPath], {
          cwd: pythonDir,
          stdio: ['pipe', 'pipe', 'pipe']
        })

        let stdout = ''
        let stderr = ''

        // Send assignments JSON to stdin
        pythonProcess.stdin.write(JSON.stringify(assignments))
        pythonProcess.stdin.end()

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString()
        })

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString()
        })

        pythonProcess.on('close', (code) => {
          console.log('=== Calendar Script Debug Info ===')
          console.log('Exit code:', code)
          console.log('stdout:', stdout)
          console.log('stderr:', stderr)
          console.log('stdout length:', stdout.length)
          console.log('stderr length:', stderr.length)
          console.log('==================================')

          // If there's no stdout but there is stderr, the error might be in stderr
          if (!stdout.trim() && stderr.trim()) {
            // Try to parse stderr as JSON (errors might be printed there)
            try {
              const errorResult = JSON.parse(stderr.trim())
              resolve(errorResult)
              return
            } catch {
              // If stderr is not JSON, return it as error details
              resolve({
                success: false,
                error: 'Python script failed',
                details: stderr.trim() || 'No output from Python script'
              })
              return
            }
          }

          // If stdout is empty, that's an error
          if (!stdout.trim()) {
            resolve({
              success: false,
              error: 'No output from Python script',
              details: stderr.trim() || 'Script produced no output'
            })
            return
          }

          try {
            // Parse JSON response
            const result = JSON.parse(stdout.trim())
            resolve(result)
          } catch (parseError) {
            // If parsing fails, return error with both stdout and stderr
            console.error('JSON parse error:', parseError)
            console.error('Attempted to parse:', stdout.trim())
            resolve({
              success: false,
              error: 'Failed to parse Python output',
              details: `stdout: ${stdout.trim()}\nstderr: ${stderr.trim()}`,
              parseError: parseError.message
            })
          }
        })

        pythonProcess.on('error', (err) => {
          reject({ success: false, error: `Failed to spawn Python process: ${err.message}` })
        })
      })
    } catch (error) {
      return { success: false, error: `Failed to add to calendar: ${error.message}` }
    }
  })

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

// In this file you can include the rest of your app"s specific main process
// code. You can also put them in separate files and require them here.
