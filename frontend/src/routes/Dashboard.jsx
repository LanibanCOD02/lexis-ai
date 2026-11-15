import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Scale, Settings, LogOut, Search, User, Menu, X, FileText, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import CaseView from '../components/CaseView';
import SourceViewer from '../components/SourceViewer';
import axios from 'axios';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeCaseId, setActiveCaseId] = useState(null);
  const [sourceData, setSourceData] = useState(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Legacy cases API removed; dashboard degraded gracefully.
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden font-sans text-foreground">
      
      {/* Mobile overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Slim, elegant sidebar */}
      <aside className={`fixed md:static inset-y-0 left-0 w-[260px] bg-surface border-r border-border flex flex-col z-50 transition-transform duration-300 ease-out ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="p-5 border-b border-border flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2.5">
            <Scale size={20} className="text-primary" />
            <span className="font-serif font-medium text-lg text-foreground tracking-tight">Lexis AI</span>
          </div>
          <button className="md:hidden text-muted hover:text-foreground transition-colors" onClick={() => setIsMobileMenuOpen(false)}>
            <X size={18} />
          </button>
        </div>
        
        <nav className="flex-1 overflow-y-auto p-3 space-y-1 mt-2">
          <div className="px-3 pb-2 text-[10px] font-semibold text-muted uppercase tracking-wider">Workspace</div>
          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md bg-muted/30 text-foreground font-medium transition-colors duration-200">
            <LayoutDashboard size={16} />
            <span className="text-sm">Research</span>
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-muted hover:bg-muted/30 hover:text-foreground font-medium transition-colors duration-200">
            <Search size={16} />
            <span className="text-sm">Case History</span>
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-md text-muted hover:bg-muted/30 hover:text-foreground font-medium transition-colors duration-200">
            <Settings size={16} />
            <span className="text-sm">Settings</span>
          </a>
        </nav>

        <div className="p-3 border-t border-border shrink-0">
          <div className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/30 transition-colors duration-200 cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-foreground text-white flex items-center justify-center shrink-0">
              <User size={14} />
            </div>
            <div className="flex flex-col flex-1 min-w-0">
              <span className="text-sm font-medium text-foreground truncate">{user?.email || 'counsel@firm.com'}</span>
              <span className="text-xs text-muted truncate">{user?.role || 'Lawyer'}</span>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 mt-1 rounded-md text-muted hover:bg-destructive/5 hover:text-destructive font-medium transition-colors duration-200"
          >
            <LogOut size={16} />
            <span className="text-sm">Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative z-10 bg-background">
        
        {/* Top Header */}
        <header className="h-14 bg-surface border-b border-border flex items-center justify-between px-4 md:px-6 shrink-0">
          <div className="flex items-center gap-3">
            <button 
              className="md:hidden p-1.5 text-muted hover:text-foreground hover:bg-muted/30 rounded-md transition-colors"
              onClick={() => setIsMobileMenuOpen(true)}
            >
              <Menu size={18} />
            </button>
            <div className="flex items-center gap-2 text-sm text-muted font-medium">
              <span>Workspace</span>
              <ChevronRight size={14} />
              <span className="text-foreground">{activeCaseId ? 'Case Analysis' : 'Upload'}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              <span className="text-xs font-medium text-muted uppercase tracking-wider">Engine Online</span>
            </div>
          </div>
        </header>

        {/* Dashboard Grid Content */}
        <div className="flex-1 flex overflow-hidden">
          <div className={`flex-1 flex flex-col overflow-y-auto ${sourceData ? 'hidden lg:flex lg:w-1/2 lg:border-r lg:border-border' : 'w-full'}`}>
            <div className="flex-1 flex flex-col w-full max-w-4xl mx-auto p-4 md:p-8 gap-8">
              
              {!activeCaseId && (
                <div className="w-full shrink-0">
                  <DocumentUpload />
                </div>
              )}

              {/* Case View (The core of the workspace) */}
              {activeCaseId ? (
                <div className="w-full shrink-0">
                  <CaseView caseId={activeCaseId} onViewSource={setSourceData} onCaseSelect={setActiveCaseId} />
                </div>
              ) : (
                <div className="flex-1 bg-surface border border-dashed border-border rounded-lg flex flex-col items-center justify-center p-12 text-center">
                  <div className="w-12 h-12 bg-muted/30 rounded-full flex items-center justify-center mb-4">
                    <FileText size={24} className="text-muted" />
                  </div>
                  <h3 className="font-serif font-medium text-xl text-foreground">No case selected</h3>
                  <p className="text-sm text-muted mt-2 max-w-sm mx-auto">
                    Upload a legal judgment or select an existing case from your history to begin AI-assisted research and extraction.
                  </p>
                </div>
              )}

              {/* Chat Interface acts as the research command center */}
              <div className="w-full shrink-0 mt-auto pt-8">
                <ChatInterface onViewSource={setSourceData} />
              </div>

            </div>
          </div>
          
          {/* Right Pane: Source Viewer (Evidence) */}
          {sourceData && (
            <div className="w-full lg:w-1/2 h-full bg-surface overflow-hidden relative z-30">
              <SourceViewer 
                documentId={sourceData.documentId}
                pageNumber={sourceData.pageNumber}
                content={sourceData.content}
                documentName={sourceData.documentName}
                onClose={() => setSourceData(null)}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
