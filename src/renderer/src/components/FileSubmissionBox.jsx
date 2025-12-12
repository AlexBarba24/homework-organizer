// eslint-disable-next-line no-unused-vars
import React, { useState } from 'react'
import axios from 'axios'

// eslint-disable-next-line react/prop-types
function FileSubmissionBox({ onSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)

  // Handles the file selection from the input
  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      alert('Please select a valid PDF file.')
    }
  }

  // Handles the drag-and-drop file input
  const handleDrop = (event) => {
    event.preventDefault()
    setIsDragging(false)
    const file = event.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      alert('Please drop a valid PDF file.')
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  // Handles the form submission
  const handleSubmit = async (event) => {
    event.preventDefault()

    if (selectedFile) {
      try {
        // Create FormData to send the file
        const formData = new FormData()
        formData.append('file', selectedFile)
        // alert('test')
        // Send the file to your server
        const response = await axios.post('http://127.0.0.1:8080/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.status !== 200) {
          throw new Error('Failed to upload file')
        }

        const data = await response.json()
        console.log('File uploaded successfully:', data)
        if (onSuccess) {
          onSuccess()
        }
      } catch (error) {
        console.error('Error uploading file:', error)
      }
    } else {
      alert('Please select or drop a file before submitting.')
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        // justifyContent: 'center',
        // alignItems: 'center',
        // height: '100vh',
        width: '120%',
        backgroundColor: '#1f2023' // Same background as the form
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem',
          width: '100%',
          maxWidth: '400px',
          margin: '0 auto',
          padding: '1rem',
          border: '1px solid #ccc',
          borderRadius: '8px',
          borderColor: 'gray',
          backgroundColor: '#2c2c2e' // Slightly darker grey
        }}
      >
        <label
          style={{
            display: 'block',
            padding: '0.5rem',
            backgroundColor: '#32362f', // Green button
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            textAlign: 'center'
          }}
        >
          Choose File
          <input
            type="file"
            onChange={handleFileChange}
            style={{
              display: 'none' // Hide the default file input
            }}
          />
        </label>

        {/* Drag-and-Drop Area */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          style={{
            width: '100%',
            height: '100px',
            border: `2px dashed ${isDragging ? '#007BFF' : '#aaa'}`, // Change border color when dragging
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: isDragging ? '#d9edf7' : '#8c8c8c', // Change background color when dragging
            color: '#353535',
            fontSize: '14px'
          }}
        >
          {isDragging ? 'Drop the file here' : 'Drag and drop a PDF file here'}
        </div>

        {/* Selected File Name */}
        {selectedFile && (
          <div
            style={{
              marginTop: '0.5rem',
              fontSize: '14px',
              color: '#fff'
            }}
          >
            Selected File: <strong>{selectedFile.name}</strong>
          </div>
        )}

        <button
          type="submit"
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#32362f', // Blue button
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Submit
        </button>
      </form>
    </div>
  )
}

export default FileSubmissionBox
