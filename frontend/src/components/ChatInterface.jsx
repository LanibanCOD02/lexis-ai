import React, { useState, useRef, useEffect } from 'react';
import { Search, Bot, User, CornerDownLeft, ChevronDown, ChevronRight, ShieldCheck, ShieldAlert, FileText, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

const EvidenceCard = ({ evidence }) => {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="mt-3 bg-surface border border-border rounded-md overflow-hidden transition-all text-[13px]">
      <button 
        onClick={() => setExpanded(!expanded)} 
        className="w-full flex items-center justify-between p-3 bg-muted/5 hover:bg-muted/10 transition-colors text-left"
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <FileText size={14} className="text-muted shrink-0" />
          <span className="font-semibold text-foreground truncate">{evidence.title || "Document"}</span>
          {evidence.citation && (
            <span className="text-muted shrink-0 font-mono text-[10px] bg-muted/20 px-1.5 py-0.5 rounded">
              {evidence.citation}
            </span>
          )}
        </div>
        <div className="shrink-0 ml-4 text-muted">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>
      </button>
      
      {expanded && (
        <div className="p-4 border-t border-border bg-background/50">
          <div className="flex flex-wrap gap-x-4 gap-y-2 mb-3 text-xs text-muted font-mono uppercase tracking-wider">
            {evidence.decision_date && <div>Date: {evidence.decision_date}</div>}
            {(evidence.page_start || evidence.page_end) && (
              <div>Pages: {evidence.page_start}{evidence.page_end && evidence.page_start !== evidence.page_end ? `-${evidence.page_end}` : ''}</div>
            )}
            {evidence.case_id && <div>ID: {evidence.case_id}</div>}
          </div>
          <div className="text-foreground leading-relaxed italic border-l-2 border-primary/30 pl-4 py-1">
            "{evidence.text}"
          </div>
        </div>
      )}
    </div>
  );
};

const VerificationBadge = ({ label, status }) => {
  const isPass = status?.toUpperCase() === 'PASS';
  const isFail = status?.toUpperCase() === 'FAIL';
  
  return (
    <div className={`flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-mono tracking-wide uppercase border ${
      isPass ? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' : 
      isFail ? 'bg-rose-500/10 text-rose-600 border-rose-500/20' : 
      'bg-muted/10 text-muted border-muted/20'
    }`}>
      {isPass ? <ShieldCheck size={12} /> : isFail ? <ShieldAlert size={12} /> : <CheckCircle2 size={12} />}
      <span>{label}: {status || 'N/A'}</span>
    </div>
  );
};

const ChatInterface = ({ onViewSource }) => {
  const [messages, setMessages] = useState([
    { 
      id: '1', 
      role: 'assistant', 
      content: "Counsel, how may I assist you with your legal research today? The Lexis AI Engine is online." 
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMsg = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Use the actual backend endpoint and payload format
      const res = await axios.post('/api/research', {
        query: userMsg.content
      });
      
      const assistantMsg = { 
        id: (Date.now() + 1).toString(), 
        role: 'assistant', 
        content: res.data.answer,
        evidence: res.data.evidence || [],
        verification: res.data.verification,
        quoteGate: res.data.quote_gate
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (error) {
      console.error(error);
      
      let errorMsg = "An unexpected error occurred while connecting to the Lexis AI Engine.";
      if (error.response) {
        if (error.response.status === 400 || error.response.status === 422) {
          errorMsg = `Validation Error: ${error.response.data.detail || "Invalid request parameters."}`;
        } else if (error.response.status === 500) {
          errorMsg = "The Lexis AI Engine encountered an internal server error during processing.";
        } else {
          errorMsg = `Server Error (${error.response.status}): The request could not be completed.`;
        }
      } else if (error.request) {
        errorMsg = "Network Error: Could not reach the Lexis AI Engine. Please check your connection or backend status.";
      }

      setMessages(prev => [...prev, { 
        id: (Date.now() + 1).toString(), 
        role: 'assistant', 
        content: errorMsg,
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface">
      <div className="flex-1 overflow-y-auto px-4 py-8 space-y-8">
        {messages.map((msg) => (
          <div key={msg.id} className="flex gap-4">
            <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-muted/20 text-muted' : msg.isError ? 'bg-rose-500/10 text-rose-500' : 'bg-primary/10 text-primary'}`}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
            </div>
            
            <div className="flex flex-col mt-1 max-w-[85%] w-full">
              {/* Answer Content */}
              <div className={`text-[15px] leading-relaxed whitespace-pre-wrap ${msg.isError ? 'text-rose-600 font-medium' : 'text-foreground'}`}>
                {msg.content}
              </div>
              
              {/* Verification Badges */}
              {(msg.quoteGate || msg.verification) && (
                <div className="flex gap-3 mt-4 mb-2">
                  {msg.quoteGate && <VerificationBadge label="Quote Gate" status={msg.quoteGate} />}
                  {msg.verification && <VerificationBadge label="Legal Verifier" status={msg.verification} />}
                </div>
              )}

              {/* Evidence Section */}
              {msg.evidence && msg.evidence.length > 0 && (
                <div className="mt-4 border-t border-border pt-4">
                  <div className="text-xs font-medium text-muted uppercase tracking-wider mb-2">
                    Verified Source Evidence ({msg.evidence.length})
                  </div>
                  <div className="space-y-2">
                    {msg.evidence.map((ev, idx) => (
                      <EvidenceCard key={idx} evidence={ev} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-4">
            <div className="shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <Bot size={14} />
            </div>
            <div className="flex flex-col gap-1 mt-1">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1.5 h-6">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-xs text-muted font-medium">Researching Supreme Court precedents & verifying citations...</span>
              </div>
              <span className="text-[11px] text-muted/70">Executing 3-way retrieval &rarr; Nemotron rerank &rarr; grounded generation &rarr; quote gate verification (~1–2 minutes).</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 pt-0 shrink-0">
        <div className="relative flex items-center bg-surface rounded-xl border border-border shadow-sm focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all">
          <Search size={18} className="absolute left-4 text-muted" />
          <textarea
            id="chat-input"
            name="chatInput"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask AI to search precedents or draft arguments..."
            className="w-full max-h-32 min-h-[56px] bg-transparent resize-none outline-none text-[15px] py-4 pl-12 pr-12 text-foreground placeholder:text-muted"
            rows={1}
          />
          <button 
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="absolute right-4 shrink-0 text-muted hover:text-primary disabled:opacity-50 disabled:hover:text-muted transition-colors"
          >
            <CornerDownLeft size={18} />
          </button>
        </div>
        <div className="mt-2 text-center text-[11px] text-muted font-medium uppercase tracking-wider">
          Lexis Deterministic Engine &bull; RRF &bull; Quote Gate
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
