import { useState } from 'react'
import GoogleAuthButton from './GoogleAuthButton'

// eslint-disable-next-line react/prop-types
function AssignmentConfirmation({ assignments, onCancel, onComplete }) {
  const [selectedAssignments, setSelectedAssignments] = useState(
    assignments.map((_, index) => index) // All selected by default
  )
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const toggleAssignment = (index) => {
    setSelectedAssignments((prev) => {
      if (prev.includes(index)) {
        return prev.filter((i) => i !== index)
      } else {
        return [...prev, index]
      }
    })
  }

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) {
        return dateString // Return original if invalid
      }
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      })
    } catch {
      return dateString
    }
  }

  const handleConfirm = async () => {
    if (selectedAssignments.length === 0) {
      setError('Please select at least one assignment to add to calendar.')
      return
    }

    if (!isAuthenticated) {
      setError('Please authenticate with Google Calendar first.')
      return
    }

    if (!window.api || !window.api.addToCalendar) {
      setError('Calendar API is not available. Please check your Electron setup.')
      return
    }

    setError(null)
    setIsLoading(true)

    try {
      // Get selected assignments
      const assignmentsToAdd = selectedAssignments.map((index) => assignments[index])

      // Call IPC API to add to calendar
      const result = await window.api.addToCalendar(assignmentsToAdd)

      if (!result.success) {
        throw new Error(result.error || 'Failed to add assignments to calendar')
      }

      setSuccess(true)
      console.log('Assignments added successfully:', result)

      // Call onComplete after a short delay to show success message
      setTimeout(() => {
        if (onComplete) {
          onComplete(result)
        }
      }, 2000)
    } catch (error) {
      console.error('Error adding to calendar:', error)
      setError(error.message || 'Failed to add assignments to calendar. Please try again.')
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    }
  }

  if (success) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem',
          padding: '2rem',
          backgroundColor: 'var(--color-background-mute)',
          borderRadius: '8px',
          color: 'var(--color-text)'
        }}
      >
        <div style={{ fontSize: '18px', color: '#4caf50' }}>✓ Success!</div>
        <div style={{ fontSize: '14px', textAlign: 'center' }}>
          Assignments have been added to your Google Calendar.
        </div>
      </div>
    )
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        width: '100%',
        maxWidth: '600px',
        margin: '0 auto',
        padding: '1.5rem',
        backgroundColor: 'var(--color-background-mute)',
        borderRadius: '8px',
        border: '1px solid var(--ev-c-gray-1)',
        minHeight: 'fit-content'
      }}
    >
      <h2 style={{ color: 'var(--color-text)', margin: '0 0 1rem 0', fontSize: '20px' }}>Review Assignments</h2>
      <p style={{ color: 'var(--ev-c-text-2)', fontSize: '14px', margin: '0 0 1rem 0' }}>
        Select the assignments you want to add to your Google Calendar:
      </p>

      {/* Google Authentication */}
      <div style={{ marginBottom: '1.5rem' }}>
        <GoogleAuthButton
          onAuthSuccess={() => {
            setIsAuthenticated(true)
            setError(null)
          }}
          onAuthError={(errorMsg) => {
            setError(errorMsg)
            setIsAuthenticated(false)
          }}
        />
      </div>

      {/* Assignments List */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem',
          maxHeight: 'calc(100vh - 500px)',
          minHeight: '200px',
          overflowY: 'auto',
          padding: '0.5rem'
        }}
      >
        {assignments.map((assignment, index) => {
          const isSelected = selectedAssignments.includes(index)
          return (
            <div
              key={index}
              onClick={() => toggleAssignment(index)}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '1rem',
                padding: '1rem',
                backgroundColor: isSelected ? 'var(--color-background)' : 'var(--color-background-soft)',
                border: `2px solid ${isSelected ? '#4caf50' : 'var(--ev-c-gray-1)'}`,
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => toggleAssignment(index)}
                onClick={(e) => e.stopPropagation()}
                style={{
                  marginTop: '0.25rem',
                  cursor: 'pointer'
                }}
              />
              <div style={{ flex: 1, color: 'var(--color-text)' }}>
                <div
                  style={{
                    fontSize: '16px',
                    fontWeight: 'bold',
                    marginBottom: '0.5rem'
                  }}
                >
                  {assignment.assignment_name || 'Untitled Assignment'}
                </div>
                <div style={{ fontSize: '14px', color: 'var(--ev-c-text-2)', marginBottom: '0.25rem' }}>
                  <strong>Due:</strong> {formatDate(assignment.due_date)}
                </div>
                {assignment.assignment_link && (
                  <div style={{ fontSize: '12px', color: 'var(--ev-c-text-3)' }}>
                    <strong>Link:</strong>{' '}
                    <a
                      href={assignment.assignment_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{ color: '#4caf50', textDecoration: 'underline' }}
                    >
                      {assignment.assignment_link}
                    </a>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Error Message */}
      {error && (
        <div
          style={{
            padding: '0.75rem',
            fontSize: '14px',
            color: '#dc2626',
            backgroundColor: 'rgba(220, 38, 38, 0.10)',
            borderRadius: '4px',
            textAlign: 'center'
          }}
        >
          {error}
        </div>
      )}

      {/* Loading Indicator */}
      {isLoading && (
        <div
          style={{
            padding: '0.75rem',
            fontSize: '14px',
            color: 'var(--color-text)',
            textAlign: 'center'
          }}
        >
          Adding assignments to calendar...
        </div>
      )}

      {/* Action Buttons */}
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          justifyContent: 'flex-end',
          marginTop: '1rem'
        }}
      >
        <button
          onClick={handleCancel}
          disabled={isLoading}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: 'var(--ev-c-gray-2)',
            color: 'var(--color-text)',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.6 : 1
          }}
        >
          Cancel
        </button>
        <button
          onClick={handleConfirm}
          disabled={isLoading || selectedAssignments.length === 0 || !isAuthenticated}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor:
              selectedAssignments.length === 0 || !isAuthenticated ? 'var(--ev-c-gray-2)' : 'var(--ev-c-gray-3)',
            color: 'var(--color-text)',
            border: 'none',
            borderRadius: '4px',
            cursor:
              isLoading || selectedAssignments.length === 0 || !isAuthenticated
                ? 'not-allowed'
                : 'pointer',
            opacity: isLoading || selectedAssignments.length === 0 || !isAuthenticated ? 0.6 : 1
          }}
        >
          {!isAuthenticated
            ? 'Authenticate First'
            : `Confirm and Add to Calendar (${selectedAssignments.length})`}
        </button>
      </div>
    </div>
  )
}

export default AssignmentConfirmation
