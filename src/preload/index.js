import { contextBridge, session } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  window.electron = electronAPI
  window.api = api
}

session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
  callback({
    responseHeaders: Object.assign(
      {
        'Content-Security-Policy': ["default-src 'self' http://127.0.0.1:8080"]
      },
      details.responseHeaders
    )
  })
})
