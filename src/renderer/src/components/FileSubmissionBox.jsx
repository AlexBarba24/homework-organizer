// eslint-disable-next-line no-unused-vars
import React, { useRef, useState } from 'react'

// eslint-disable-next-line react/prop-types
function FileSubmissionBox({ onParseComplete }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const clearSelectedFile = () => {
    setSelectedFile(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // Handles the file selection from the input
  const handleFileChange = (event) => {
    setError(null)
    const file = event.target.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      setSelectedFile(null)
      setError('Please select a valid PDF file.')
    }
  }

  // Handles the drag-and-drop file input
  const handleDrop = (event) => {
    event.preventDefault()
    if (isLoading) return
    setIsDragging(false)
    setError(null)
    const file = event.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      setSelectedFile(null)
      setError('Please drop a valid PDF file.')
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    if (!isLoading) setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  // Handles the form submission
  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)

    if (!selectedFile) {
      setError('Please select or drop a file before submitting.')
      return
    }

    if (!window.api || !window.api.parsePdf) {
      setError('PDF parsing API is not available. Please check your Electron setup.')
      return
    }

    setIsLoading(true)

    try {
      // Read file as ArrayBuffer
      const arrayBuffer = await selectedFile.arrayBuffer()
      const fileBuffer = Array.from(new Uint8Array(arrayBuffer))

      // Call IPC API to parse PDF
      const assignments = await window.api.parsePdf(fileBuffer)

      // Check for error response
      if (assignments && assignments.error) {
        // Format error message with details
        let errorMessage = assignments.error
        if (assignments.details) {
          // For Python errors, show a more user-friendly message
          if (
            assignments.details.includes('ImportError') ||
            assignments.details.includes('Library not loaded')
          ) {
            errorMessage = `${assignments.error}\n\nThis appears to be a Python dependency issue. Please check your Python environment and install missing dependencies.`
          } else {
            errorMessage = `${assignments.error}\n\n${assignments.details}`
          }
        }
        throw new Error(errorMessage)
      }

      // Validate assignments array
      if (!Array.isArray(assignments)) {
        throw new Error('Invalid response from PDF parser')
      }

      console.log('PDF parsed successfully. Found', assignments.length, 'assignments')

      // Pass parsed assignments to parent component
      if (onParseComplete) {
        onParseComplete(assignments)
      }
    } catch (error) {
      console.error('Error parsing PDF:', error)
      setError(error.message || 'Failed to parse PDF. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="upload-shell">
      <form onSubmit={handleSubmit} className="upload-card">
        <label className="upload-choose" aria-disabled={isLoading}>
          <span className="upload-choose-text">Select a PDF</span>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={isLoading}
            style={{ display: 'none' }}
          />
        </label>

        <div className="upload-help" aria-live="polite">
          Drag and drop a PDF, or click to browse. <span className="upload-help-muted">PDF only.</span>
        </div>

        {/* Drag-and-Drop Area */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => {
            if (isLoading) return
            fileInputRef.current?.click()
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              fileInputRef.current?.click()
            }
          }}
          tabIndex={0}
          role="button"
          aria-label="Upload PDF by drag and drop or selecting a file"
          style={{
            // Kept for layout compatibility; actual styling handled by CSS below.
            width: '100%'
          }}
          className={`upload-dropzone ${isDragging ? 'is-dragging' : ''}`}
        >
          <div className="upload-dropzone-content">
            <div className="upload-dropzone-title">
              {isDragging ? 'Drop the file here' : 'Drag & drop your PDF'}
            </div>
            <div className="upload-dropzone-subtitle">
              {isLoading ? 'Parsing…' : 'No file selected yet'}
            </div>
          </div>
        </div>

        {/* Selected File */}
        {selectedFile && (
          <div className="upload-file-row" aria-live="polite">
            <div className="upload-file-pill" title={selectedFile.name}>
              <span className="upload-file-ext">PDF</span>
              <span className="upload-file-name">{selectedFile.name}</span>
            </div>
            <button
              type="button"
              className="upload-remove"
              onClick={clearSelectedFile}
              disabled={isLoading}
              aria-label="Remove selected file"
            >
              Remove
            </button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="upload-error" role="alert">
            {error}
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="upload-loading" aria-live="polite">
            <span className="upload-spinner" aria-hidden="true" />
            Parsing PDF... This may take a moment.
          </div>
        )}

        <button type="submit" className="upload-submit" disabled={isLoading || !selectedFile}>
          {isLoading ? 'Processing...' : 'Parse PDF'}
        </button>
      </form>
    </div>
  )
}

export default FileSubmissionBox
