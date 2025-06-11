import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload = ({ onFileUpload }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  // Supported file types
  const supportedTypes = {
    'application/pdf': 'PDF Document',
    'text/plain': 'Text File',
    'text/markdown': 'Markdown File',
    'image/png': 'PNG Image',
    'image/jpeg': 'JPEG Image',
    'image/jpg': 'JPG Image',
    'image/gif': 'GIF Image',
    'application/msword': 'Word Document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word Document'
  };

  const maxFileSize = 10 * 1024 * 1024; // 10MB

  const validateFile = (file) => {
    if (!supportedTypes[file.type]) {
      return `Unsupported file type: ${file.type}`;
    }
    if (file.size > maxFileSize) {
      return `File too large: ${(file.size / 1024 / 1024).toFixed(1)}MB (max 10MB)`;
    }
    return null;
  };

  const handleFiles = async (files) => {
    const fileArray = Array.from(files);
    const validFiles = [];
    const errors = [];

    // Validate each file
    fileArray.forEach(file => {
      const error = validateFile(file);
      if (error) {
        errors.push(`${file.name}: ${error}`);
      } else {
        validFiles.push(file);
      }
    });

    // Show errors if any
    if (errors.length > 0) {
      alert(`Upload errors:\n${errors.join('\n')}`);
    }

    // Process valid files
    if (validFiles.length > 0) {
      setUploading(true);
      try {
        for (const file of validFiles) {
          await uploadFile(file);
        }
      } catch (error) {
        console.error('Upload error:', error);
        alert(`Upload failed: ${error.message}`);
      } finally {
        setUploading(false);
      }
    }
  };

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      // For now, we'll simulate upload since backend endpoint might not exist yet
      // TODO: Replace with actual backend endpoint when implemented
      const response = await fetch('http://127.0.0.1:8001/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const result = await response.json();
      
      const fileInfo = {
        id: Date.now() + Math.random(),
        name: file.name,
        type: file.type,
        size: file.size,
        uploadedAt: new Date().toISOString(),
        url: result.url || URL.createObjectURL(file), // Fallback to blob URL
      };

      setUploadedFiles(prev => [...prev, fileInfo]);
      
      // Notify parent component
      if (onFileUpload) {
        onFileUpload(fileInfo);
      }

    } catch (error) {
      // If upload endpoint doesn't exist, store locally for now
      console.warn('Upload endpoint not available, storing locally:', error);
      
      const fileInfo = {
        id: Date.now() + Math.random(),
        name: file.name,
        type: file.type,
        size: file.size,
        uploadedAt: new Date().toISOString(),
        url: URL.createObjectURL(file),
        local: true, // Flag to indicate this is stored locally
      };

      setUploadedFiles(prev => [...prev, fileInfo]);
      
      if (onFileUpload) {
        onFileUpload(fileInfo);
      }
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return '🖼️';
    if (type === 'application/pdf') return '📄';
    if (type.startsWith('text/')) return '📝';
    if (type.includes('word')) return '📘';
    return '📎';
  };

  return (
    <div className="file-upload">
      <h4>File & Document Upload</h4>
      
      <div 
        className={`upload-zone ${dragActive ? 'drag-active' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.md,.png,.jpg,.jpeg,.gif,.doc,.docx"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        
        <div className="upload-content">
          {uploading ? (
            <>
              <div className="upload-spinner">⏳</div>
              <p>Uploading files...</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📁</div>
              <p><strong>Click to upload</strong> or drag and drop</p>
              <p className="upload-hint">
                PDFs, images, text files, Word docs (max 10MB each)
              </p>
            </>
          )}
        </div>
      </div>

      <div className="supported-formats">
        <p><strong>Supported formats:</strong></p>
        <div className="format-tags">
          <span>PDF</span>
          <span>TXT</span>
          <span>MD</span>
          <span>PNG</span>
          <span>JPG</span>
          <span>GIF</span>
          <span>DOC</span>
          <span>DOCX</span>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h5>Uploaded Files ({uploadedFiles.length})</h5>
          <div className="file-list">
            {uploadedFiles.map(file => (
              <div key={file.id} className="file-item">
                <div className="file-info">
                  <span className="file-icon">{getFileIcon(file.type)}</span>
                  <div className="file-details">
                    <span className="file-name">{file.name}</span>
                    <span className="file-meta">
                      {formatFileSize(file.size)} • {new Date(file.uploadedAt).toLocaleTimeString()}
                      {file.local && <span className="local-badge">Local</span>}
                    </span>
                  </div>
                </div>
                <button 
                  className="remove-file"
                  onClick={() => removeFile(file.id)}
                  title="Remove file"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 