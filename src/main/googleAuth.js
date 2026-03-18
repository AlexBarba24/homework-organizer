import { google } from 'googleapis'
import { join } from 'path'
import { readFile, writeFile } from 'fs/promises'
import { existsSync } from 'fs'
import { BrowserWindow } from 'electron'
import { is } from '@electron-toolkit/utils'

const SCOPES = [
  'https://www.googleapis.com/auth/calendar',
  'https://www.googleapis.com/auth/calendar.readonly'
]

export function getCredentialsPath() {
  // Try multiple possible locations in order of preference
  const possiblePaths = []

  if (is.dev) {
    // In development, __dirname is out/main/, so go up to project root then into src/python
    possiblePaths.push(join(__dirname, '../../src/python/credentials.json'))
    // Also try app.getAppPath() in case it points to project root
    const { app } = require('electron')
    possiblePaths.push(join(app.getAppPath(), 'src/python/credentials.json'))
  } else {
    // In production, try multiple possible locations
    const { app } = require('electron')
    const appPath = app.getAppPath()
    possiblePaths.push(join(appPath, '../app.asar.unpacked/src/python/credentials.json'))
    possiblePaths.push(join(appPath, '../resources/src/python/credentials.json'))
    possiblePaths.push(join(appPath, 'src/python/credentials.json'))
    possiblePaths.push(join(appPath, 'python/credentials.json'))
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

export function getTokenPath() {
  // Try multiple possible locations in order of preference
  const possiblePaths = []

  if (is.dev) {
    // In development, __dirname is out/main/, so go up to project root then into src/python
    possiblePaths.push(join(__dirname, '../../src/python/token.json'))
    // Also try app.getAppPath() in case it points to project root
    const { app } = require('electron')
    possiblePaths.push(join(app.getAppPath(), 'src/python/token.json'))
  } else {
    // In production, try multiple possible locations
    const { app } = require('electron')
    const appPath = app.getAppPath()
    possiblePaths.push(join(appPath, '../app.asar.unpacked/src/python/token.json'))
    possiblePaths.push(join(appPath, '../resources/src/python/token.json'))
    possiblePaths.push(join(appPath, 'src/python/token.json'))
    possiblePaths.push(join(appPath, 'python/token.json'))
  }

  // Try each path and return the first one that exists, or the first one if none exist
  for (const path of possiblePaths) {
    if (existsSync(path)) {
      return path
    }
  }

  // If none exist, return the first one (will be used for saving new tokens)
  return possiblePaths[0]
}

export async function loadCredentials() {
  // First, try environment variables (for CI/CD builds or secure deployments)
  if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
    console.log('Loading credentials from environment variables')
    return {
      installed: {
        client_id: process.env.GOOGLE_CLIENT_ID,
        client_secret: process.env.GOOGLE_CLIENT_SECRET,
        redirect_uris: [process.env.GOOGLE_REDIRECT_URI || 'http://localhost'],
        project_id: process.env.GOOGLE_PROJECT_ID || 'homework-organizer',
        auth_uri: 'https://accounts.google.com/o/oauth2/auth',
        token_uri: 'https://oauth2.googleapis.com/token',
        auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs'
      }
    }
  }

  // Fallback to credentials.json file
  const credentialsPath = getCredentialsPath()
  console.log('=== Google Auth Debug Info ===')
  console.log('Is dev mode:', is.dev)
  console.log('__dirname:', __dirname)
  console.log('Looking for credentials.json at:', credentialsPath)
  console.log('File exists:', existsSync(credentialsPath))
  console.log('================================')

  if (!existsSync(credentialsPath)) {
    throw new Error(
      `credentials.json not found at: ${credentialsPath}\n\n` +
        'To fix this:\n' +
        '1. Copy credentials.json.example to credentials.json:\n' +
        '   cp src/python/credentials.json.example src/python/credentials.json\n' +
        '2. Go to Google Cloud Console (https://console.cloud.google.com/)\n' +
        '3. Create or select a project\n' +
        '4. Enable Google Calendar API\n' +
        '5. Create OAuth 2.0 credentials (Desktop app)\n' +
        '6. Download the credentials file\n' +
        '7. Replace the placeholder values in src/python/credentials.json\n\n' +
        'Alternatively, set environment variables:\n' +
        '  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI'
    )
  }
  const content = await readFile(credentialsPath, 'utf8')
  return JSON.parse(content)
}

export async function loadToken() {
  const tokenPath = getTokenPath()
  if (!existsSync(tokenPath)) {
    return null
  }
  try {
    const content = await readFile(tokenPath, 'utf8')
    return JSON.parse(content)
  } catch (error) {
    console.error('Error loading token:', error)
    return null
  }
}

export async function saveToken(token) {
  const tokenPath = getTokenPath()

  // Ensure token is in format compatible with both JavaScript (googleapis) and Python (google-auth)
  // Python's Credentials.from_authorized_user_file expects:
  // - token (access_token) - Python uses 'token', googleapis uses 'access_token'
  // - refresh_token
  // - token_uri
  // - client_id
  // - client_secret
  // - scopes (array of strings)

  // Transform token format to be compatible with Python's google-auth library
  const tokenToSave = {
    ...token,
    // Python expects 'token' instead of 'access_token'
    token: token.access_token || token.token,
    // Ensure scopes is an array of strings
    scopes: token.scope
      ? Array.isArray(token.scope)
        ? token.scope
        : token.scope.split(' ')
      : SCOPES
  }

  // Keep both token and access_token for compatibility
  // JavaScript (googleapis) uses access_token, Python (google-auth) uses token
  if (
    tokenToSave.token &&
    tokenToSave.access_token &&
    tokenToSave.token === tokenToSave.access_token
  ) {
    // Both are present and identical - this is fine for compatibility
  }

  await writeFile(tokenPath, JSON.stringify(tokenToSave, null, 2))
  console.log('Token saved to:', tokenPath, '(compatible with both JavaScript and Python)')
}

export function createOAuth2Client(credentials) {
  const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web
  return new google.auth.OAuth2(client_id, client_secret, redirect_uris?.[0] || 'http://localhost')
}

export async function checkAuthentication() {
  try {
    const credentials = await loadCredentials()
    const token = await loadToken()

    if (!token) {
      return { authenticated: false, needsAuth: true }
    }

    const oAuth2Client = createOAuth2Client(credentials)
    oAuth2Client.setCredentials(token)

    // Try to refresh if expired
    if (token.expiry_date && token.expiry_date < Date.now()) {
      if (token.refresh_token) {
        try {
          const { credentials: newCredentials } = await oAuth2Client.refreshAccessToken()
          oAuth2Client.setCredentials(newCredentials)
          await saveToken(newCredentials)
          return { authenticated: true, tokenRefreshed: true }
        } catch (error) {
          console.error('Error refreshing token:', error)
          return { authenticated: false, needsAuth: true, error: 'Token refresh failed' }
        }
      } else {
        return {
          authenticated: false,
          needsAuth: true,
          error: 'Token expired and no refresh token'
        }
      }
    }

    return { authenticated: true }
  } catch (error) {
    console.error('Error checking authentication:', error)
    return { authenticated: false, needsAuth: true, error: error.message }
  }
}

export async function getAuthUrl() {
  const credentials = await loadCredentials()
  const oAuth2Client = createOAuth2Client(credentials)

  return oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent' // Force consent screen to get refresh token
  })
}

export async function authenticateWithCode(code) {
  try {
    // Validate code
    if (!code || typeof code !== 'string' || !code.trim()) {
      throw new Error('Invalid authorization code')
    }

    const credentials = await loadCredentials()
    const oAuth2Client = createOAuth2Client(credentials)

    const trimmedCode = code.trim()
    console.log('Exchanging authorization code for token...')
    console.log('Using redirect URI:', oAuth2Client.redirectUri)

    const { tokens } = await oAuth2Client.getToken(trimmedCode)
    oAuth2Client.setCredentials(tokens)

    // Save token - the format from googleapis is already compatible with Python's google-auth
    // Both libraries use the same OAuth 2.0 token format
    console.log('Saving token...')
    await saveToken(tokens)
    console.log('Token saved successfully and is compatible with both JavaScript and Python')

    return { success: true, tokens }
  } catch (error) {
    console.error('Error authenticating with code:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status
    })

    let errorMessage = error.message
    if (error.response?.data?.error_description) {
      errorMessage = `${error.response.data.error}: ${error.response.data.error_description}`
    }
    return { success: false, error: errorMessage }
  }
}

export async function authenticateWithBrowser(mainWindow) {
  try {
    const authUrl = await getAuthUrl()
    console.log('Opening authentication URL')
    return new Promise((resolve, reject) => {
      let codeProcessed = false // Flag to prevent double processing
      let authWindow = null

      // Create auth window
      authWindow = new BrowserWindow({
        width: 500,
        height: 600,
        parent: mainWindow,
        modal: true,
        show: false,
        webPreferences: {
          nodeIntegration: false,
          contextIsolation: true
        }
      })

      authWindow.loadURL(authUrl)
      authWindow.show()

      // Shared function to process the authorization code (only once)
      const processCode = async (code) => {
        if (codeProcessed) {
          console.log('Authorization code already processed, ignoring duplicate attempt')
          return
        }

        if (!code || !code.trim()) {
          console.error('Empty or invalid authorization code received')
          if (!codeProcessed) {
            reject(new Error('No authorization code received'))
          }
          return
        }

        codeProcessed = true
        const trimmedCode = code.trim()
        console.log('Processing authorization code (length:', trimmedCode.length, ')')

        // Close window before processing to prevent further events
        if (authWindow && !authWindow.isDestroyed()) {
          authWindow.close()
        }

        try {
          const result = await authenticateWithCode(trimmedCode)
          if (result.success) {
            console.log('Authentication successful, token saved')
            resolve(result)
          } else {
            reject(new Error(result.error))
          }
        } catch (err) {
          console.error('Error in processCode:', err)
          reject(err)
        }
      }

      // Handle navigation to catch the redirect
      authWindow.webContents.on('will-redirect', async (event, navigationUrl) => {
        console.log('will-redirect event to:', navigationUrl)
        try {
          const url = new URL(navigationUrl)
          if (url.searchParams.has('code')) {
            event.preventDefault()
            const code = url.searchParams.get('code')
            await processCode(code)
          } else if (url.searchParams.has('error')) {
            const error = url.searchParams.get('error')
            const errorDesc = url.searchParams.get('error_description')
            if (authWindow && !authWindow.isDestroyed()) {
              authWindow.close()
            }
            if (!codeProcessed) {
              reject(new Error(`Authentication failed: ${error} - ${errorDesc || ''}`))
            }
          }
        } catch (err) {
          console.error('Error parsing redirect URL:', err)
        }
      })

      // Also check for code in the URL after navigation
      authWindow.webContents.on('did-navigate', async (event, url) => {
        console.log('did-navigate event to:', url)
        try {
          const urlObj = new URL(url)
          if (urlObj.searchParams.has('code')) {
            const code = urlObj.searchParams.get('code')
            await processCode(code)
          } else if (urlObj.searchParams.has('error')) {
            const error = urlObj.searchParams.get('error')
            const errorDesc = urlObj.searchParams.get('error_description')
            if (authWindow && !authWindow.isDestroyed()) {
              authWindow.close()
            }
            if (!codeProcessed) {
              reject(new Error(`Authentication failed: ${error} - ${errorDesc || ''}`))
            }
          }
        } catch (err) {
          console.error('Error parsing navigation URL:', err)
        }
      })

      authWindow.on('closed', () => {
        if (!codeProcessed) {
          reject(new Error('Authentication window closed'))
        }
      })
    })
  } catch (error) {
    return Promise.reject(error)
  }
}
