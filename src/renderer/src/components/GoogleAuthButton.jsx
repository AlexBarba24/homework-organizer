import { useState, useEffect } from 'react'

function GoogleAuthButton({ onAuthSuccess, onAuthError }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isChecking, setIsChecking] = useState(true)
  const [isAuthenticating, setIsAuthenticating] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    setIsChecking(true)
    setError(null)
    try {
      if (!window.api || !window.api.checkGoogleAuth) {
        setError('Google Auth API is not available')
        setIsChecking(false)
        return
      }

      const result = await window.api.checkGoogleAuth()
      const wasAuthenticated = isAuthenticated
      setIsAuthenticated(result.authenticated)

      // Notify parent if authentication status changed
      if (result.authenticated && !wasAuthenticated && onAuthSuccess) {
        onAuthSuccess()
      } else if (!result.authenticated && wasAuthenticated) {
        // Authentication was lost
        if (onAuthError) {
          onAuthError('Authentication expired or was revoked')
        }
      }

      if (result.error) {
        setError(result.error)
      }
    } catch (err) {
      console.error('Error checking auth status:', err)
      setError(err.message || 'Failed to check authentication status')
    } finally {
      setIsChecking(false)
    }
  }

  const handleAuthenticate = async () => {
    setIsAuthenticating(true)
    setError(null)

    try {
      if (!window.api || !window.api.authenticateGoogle) {
        throw new Error('Google Auth API is not available')
      }

      const result = await window.api.authenticateGoogle()

      if (result.success) {
        setIsAuthenticated(true)
        // Re-check auth status to get updated token info
        await checkAuthStatus()
        // onAuthSuccess will be called by checkAuthStatus if needed
      } else {
        throw new Error(result.error || 'Authentication failed')
      }
    } catch (err) {
      console.error('Error authenticating:', err)
      const errorMessage = err.message || 'Failed to authenticate with Google'
      setError(errorMessage)
      if (onAuthError) {
        onAuthError(errorMessage)
      }
    } finally {
      setIsAuthenticating(false)
    }
  }

  if (isChecking) {
    return (
      <div
        style={{
          padding: '1rem',
          textAlign: 'center',
          color: 'var(--color-text)',
          fontSize: '14px'
        }}
      >
        Checking authentication...
      </div>
    )
  }

  if (isAuthenticated) {
    return (
      <div
        style={{
          padding: '1rem',
          backgroundColor: 'var(--color-background-mute)',
          borderRadius: '6px',
          border: '1px solid #4caf50',
          color: 'var(--color-text)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ color: '#4caf50', fontSize: '18px' }}>✓</span>
          <span>Connected to Google Calendar</span>
        </div>
        <button
          onClick={checkAuthStatus}
          style={{
            marginTop: '0.5rem',
            padding: '0.5rem 1rem',
            backgroundColor: 'var(--ev-c-gray-2)',
            color: 'var(--color-text)',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Refresh Status
        </button>
      </div>
    )
  }

  return (
    <div
      style={{
        padding: '1rem',
        backgroundColor: 'var(--color-background-mute)',
        borderRadius: '6px',
        border: '1px solid var(--ev-c-gray-1)'
      }}
    >
      <div style={{ marginBottom: '1rem', color: 'var(--color-text)' }}>
        <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '16px' }}>
          Google Calendar Authentication Required
        </h3>
        <p style={{ margin: 0, fontSize: '14px', color: 'var(--ev-c-text-2)' }}>
          You need to authenticate with Google Calendar to add assignments.
        </p>
      </div>

      {error && (
        <div
          style={{
            marginBottom: '1rem',
            padding: '0.75rem',
            backgroundColor: 'rgba(220, 38, 38, 0.10)',
            border: '1px solid rgba(220, 38, 38, 0.22)',
            borderRadius: '4px',
            color: '#dc2626',
            fontSize: '14px'
          }}
        >
          {error}
        </div>
      )}

      <button
        onClick={handleAuthenticate}
        disabled={isAuthenticating}
        style={{
          width: '100%',
          padding: '0.75rem 1.5rem',
          backgroundColor: isAuthenticating ? 'var(--ev-c-gray-2)' : '#4285f4',
          color: isAuthenticating ? 'var(--color-text)' : 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: isAuthenticating ? 'not-allowed' : 'pointer',
          fontSize: '14px',
          fontWeight: 'bold',
          opacity: isAuthenticating ? 0.6 : 1
        }}
      >
        {isAuthenticating ? 'Authenticating...' : 'Connect to Google Calendar'}
      </button>
    </div>
  )
}

export default GoogleAuthButton
