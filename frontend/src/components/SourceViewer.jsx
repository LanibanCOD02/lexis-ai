import React, { useState, useEffect } from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { searchPlugin } from '@react-pdf-viewer/search';
import { Loader2, AlertCircle, X } from 'lucide-react';
import axios from 'axios';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import '@react-pdf-viewer/search/lib/styles/index.css';

const SourceViewer = ({ documentId, pageNumber, content, documentName, onClose }) => {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [highlightError, setHighlightError] = useState(false);

  const searchPluginInstance = searchPlugin();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const { highlight } = searchPluginInstance;

  useEffect(() => {
    if (!documentId) return;

    let objectUrl = null;
    const fetchPdf = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`/api/v1/documents/${documentId}/file`, {
          responseType: 'blob'
        });
        objectUrl = URL.createObjectURL(response.data);
        setPdfUrl(objectUrl);
      } catch (err) {
        console.error("Error fetching PDF", err);
        setError("Failed to load the document.");
      } finally {
        setLoading(false);
      }
    };

    fetchPdf();

    return () => {
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [documentId]);

  const handleDocumentLoad = (e) => {
    if (pageNumber) {
      setTimeout(() => {
        if (content) {
          const cleanContent = content.split('\n---\n').pop().trim();
          
          highlight({
            keyword: cleanContent,
            matchCase: false,
            wholeWords: false,
          }).then((matches) => {
              if (matches && matches.length > 0) {
                  setHighlightError(false);
              } else {
                  const smallerSnippet = cleanContent.substring(0, 50).trim();
                  highlight({
                    keyword: smallerSnippet,
                    matchCase: false,
                    wholeWords: false,
                  }).then((fallbackMatches) => {
                       if (fallbackMatches && fallbackMatches.length > 0) {
                            setHighlightError(false);
                       } else {
                            setHighlightError(true);
                       }
                  });
              }
          });
        }
      }, 500);
    }
  };

  if (!documentId) return null;

  return (
    <div className="flex flex-col h-full bg-surface">
      {/* Header */}
      <div className="h-14 px-4 border-b border-border bg-surface flex justify-between items-center shrink-0">
        <div className="flex flex-col">
          <h3 className="font-serif font-medium text-[15px] text-foreground leading-none">Source Evidence</h3>
          <p className="text-[11px] text-muted mt-1 truncate max-w-[200px] md:max-w-xs">{documentName || 'Loading...'}</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="p-1.5 text-muted hover:text-foreground hover:bg-muted/10 rounded-md transition-colors">
            <X size={16} />
          </button>
        )}
      </div>

      {highlightError && (
        <div className="bg-yellow-50 text-yellow-800 p-2.5 text-xs flex items-center gap-2 border-b border-yellow-100 font-medium">
          <AlertCircle size={14} />
          <span>Source passage could not be highlighted exactly. The correct page is shown.</span>
        </div>
      )}

      {/* Viewer Area */}
      <div className="flex-1 relative bg-muted/10">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/80 backdrop-blur-sm z-10">
             <div className="flex flex-col items-center gap-3">
                <Loader2 className="animate-spin text-muted" size={24} />
                <span className="text-sm font-medium text-muted">Retrieving document...</span>
             </div>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/80 backdrop-blur-sm z-10 text-destructive font-medium flex-col gap-3 text-center px-4">
             <AlertCircle size={24} />
             <p>{error}</p>
          </div>
        )}

        {pdfUrl && (
          <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
            <Viewer
              fileUrl={pdfUrl}
              plugins={[defaultLayoutPluginInstance, searchPluginInstance]}
              onDocumentLoad={handleDocumentLoad}
              initialPage={pageNumber ? Math.max(0, pageNumber - 1) : 0}
            />
          </Worker>
        )}
      </div>
    </div>
  );
};

export default SourceViewer;
