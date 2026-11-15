import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const DocumentUpload = ({ onUploadComplete }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [errorMsg, setErrorMsg] = useState('');
  const { token } = useAuth();
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    if (selectedFile.type !== 'application/pdf') {
      setStatus('error');
      setErrorMsg('Only PDF files are supported.');
      return;
    }
    setFile(selectedFile);
    uploadFile(selectedFile);
  };

  const uploadFile = async (selectedFile) => {
    setStatus('uploading');
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await axios.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });
      setStatus('success');
      if (onUploadComplete) onUploadComplete(res.data);
      
      setTimeout(() => {
        setStatus('idle');
        setFile(null);
      }, 3000);
    } catch (err) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err.response?.data?.detail || 'An error occurred during upload.');
    }
  };

  return (
    <div className="w-full">
      <div 
        className={`relative flex flex-col items-center justify-center p-10 border border-dashed rounded-md transition-all duration-300 ease-out cursor-pointer ${
          dragActive ? 'border-primary bg-muted/20' : 'border-border bg-surface hover:bg-muted/10 hover:border-muted'
        } ${status === 'uploading' ? 'opacity-70 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => status === 'idle' && inputRef.current?.click()}
      >
        <input 
          id="file-upload"
          name="fileUpload"
          ref={inputRef}
          type="file" 
          className="hidden" 
          accept="application/pdf"
          onChange={handleChange}
        />
        
        {status === 'idle' && (
          <div className="flex flex-col items-center gap-3 text-center">
            <UploadCloud size={20} className="text-muted" />
            <div>
              <p className="text-sm font-medium text-foreground">Upload Judgment</p>
              <p className="text-xs text-muted mt-1">Drag and drop a PDF file here, or click to browse.</p>
            </div>
          </div>
        )}

        {status === 'uploading' && (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="animate-spin text-muted" size={20} />
            <p className="text-sm font-medium text-muted">Ingesting & Vectorizing...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle size={20} className="text-green-600" />
            <p className="text-sm font-medium text-foreground">Document Indexed Successfully</p>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center gap-3 text-center">
            <AlertCircle size={20} className="text-destructive" />
            <div>
              <p className="text-sm font-medium text-foreground">{errorMsg}</p>
              <button 
                onClick={(e) => { e.stopPropagation(); setStatus('idle'); }}
                className="mt-1 text-xs font-medium text-primary hover:text-foreground transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentUpload;
