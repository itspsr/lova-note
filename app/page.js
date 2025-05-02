"use client";

import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';

const TranscriberApp = () => {
  const [transcribing, setTranscribing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [filePreview, setFilePreview] = useState(null);
  const [files, setFiles] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('en');

  // Drag-and-drop setup
  const { getRootProps, getInputProps } = useDropzone({
    onDrop: (acceptedFiles) => {
      setFiles(acceptedFiles);
      setFilePreview(URL.createObjectURL(acceptedFiles[0]));
    },
  });

  // Handle file change (for both drag-and-drop and file picker)
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFiles([file]);
      setFilePreview(URL.createObjectURL(file));
    }
  };

  // Handle language selection
  const handleLanguageChange = (e) => {
    setSelectedLanguage(e.target.value);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    // Ensure file is correctly appended with the name 'audio'
    files.forEach((file) => formData.append('audio', file));
    formData.append('language', selectedLanguage);

    setTranscribing(true);
    setTranscription('');
    setError(null);
    setProgress(0); // Reset progress bar

    try {
      const response = await fetch('/api/transcribe', {
        method: 'POST',
        body: formData,
        headers: {
          // Do not manually set 'Content-Type', it will be set automatically for multipart/form-data
        },
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let partialText = '';
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        partialText += decoder.decode(value, { stream: true });

        // Check if there's progress information in the response
        if (partialText.includes('Progress:')) {
          const match = partialText.match(/Progress:\s*(\d+)%/);
          if (match) {
            setProgress(parseInt(match[1]));
            partialText = ''; // Clear the buffer
          }
        }

        // If the response contains the full transcription
        if (partialText.includes('Transcription:')) {
          setTranscription(partialText);
          break;
        }
      }
    } catch (err) {
      setError('Something went wrong');
    } finally {
      setTranscribing(false);
      setProgress(0); // Reset progress after finishing
    }
  };

  const handleClear = () => {
    setTranscription('');
    setFiles([]);
    setFilePreview(null);
    setProgress(0);
    setError(null);
  };

  return (
    <div
      style={{
        backgroundColor: '#1A1A1A',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        padding: '20px',
      }}
    >
      <h1 style={{ fontSize: '2rem', marginBottom: '20px' }}>LovaNote Transcriber</h1>

      {/* Drag-and-drop area */}
      <div
        {...getRootProps()}
        style={{
          border: '2px dashed #4CAF50',
          padding: '40px',
          borderRadius: '8px',
          cursor: 'pointer',
          textAlign: 'center',
          marginBottom: '20px',
        }}
      >
        <input {...getInputProps()} />
        <p>Drag & drop your audio file here, or click to select one.</p>
      </div>

      {/* File preview */}
      {filePreview && (
        <div style={{ marginBottom: '20px' }}>
          <p>Selected file: {files[0].name}</p>
          <audio controls src={filePreview}></audio>
        </div>
      )}

      {/* Language selector */}
      <select
        value={selectedLanguage}
        onChange={handleLanguageChange}
        style={{
          padding: '10px',
          fontSize: '1rem',
          marginBottom: '20px',
          borderRadius: '8px',
          border: '1px solid #ccc',
          backgroundColor: '#2C3E50',
          color: 'white',
        }}
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="ml">Malayalam</option>
        <option value="ta">Tamil</option>
        {/* Add more languages as needed */}
      </select>

      {/* Upload button */}
      <button
        onClick={handleUpload}
        style={{
          backgroundColor: '#4CAF50',
          padding: '10px 20px',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: 'bold',
          marginBottom: '20px',
          transition: 'background-color 0.3s',
        }}
      >
        {transcribing ? 'Transcribing...' : 'Start Transcription'}
      </button>

      {/* Clear button */}
      <button
        onClick={handleClear}
        style={{
          backgroundColor: '#E74C3C',
          padding: '10px 20px',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: 'bold',
          marginBottom: '20px',
          transition: 'background-color 0.3s',
        }}
      >
        Clear
      </button>

      {/* Progress bar */}
      {transcribing && (
        <div style={{ width: '100%', backgroundColor: '#ccc', borderRadius: '8px' }}>
          <div
            style={{
              height: '10px',
              width: `${progress}%`,
              backgroundColor: '#4CAF50',
              borderRadius: '8px',
            }}
          ></div>
        </div>
      )}

      {/* Transcription result */}
      {transcription && (
        <div
          style={{
            backgroundColor: '#2C3E50',
            padding: '15px',
            borderRadius: '10px',
            maxWidth: '90%',
            marginTop: '20px',
          }}
        >
          <h2>Transcription:</h2>
          <p>{transcription}</p>
        </div>
      )}

      {/* Error message */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default TranscriberApp;
