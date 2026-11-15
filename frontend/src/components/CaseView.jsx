import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FileText, List, Loader2, BookOpen, Scale, ExternalLink, Search, Network } from 'lucide-react';
import CitationNetworkGraph from './CitationNetworkGraph';

const CaseView = ({ caseId, onViewSource, onCaseSelect }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loadingSourceId, setLoadingSourceId] = useState(null);
  
  const [summary, setSummary] = useState(null);
  const [principles, setPrinciples] = useState(null);
  const [similarCases, setSimilarCases] = useState(null);
  const [citations, setCitations] = useState([]);
  const [citedBy, setCitedBy] = useState([]);
  
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [isLoadingPrinciples, setIsLoadingPrinciples] = useState(false);
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(false);
  const [isLoadingCitations, setIsLoadingCitations] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (caseId) {
      setSummary(null);
      setPrinciples(null);
      setSimilarCases(null);
      setCitations([]);
      setCitedBy([]);
      setActiveTab('overview');
      fetchSummary();
      fetchPrinciples();
      fetchCitations();
    }
  }, [caseId]);

  const fetchSummary = async () => {
    try {
      const res = await axios.get(`/api/v1/cases/${caseId}/summary`);
      setSummary(res.data);
    } catch (err) {
      if (err.response?.status !== 404) {
        console.error('Error fetching summary', err);
      }
    }
  };

  const fetchPrinciples = async () => {
    try {
      const res = await axios.get(`/api/v1/cases/${caseId}/principles`);
      if (res.data && res.data.length > 0) {
        setPrinciples(res.data);
      }
    } catch (err) {
      console.error('Error fetching principles', err);
    }
  };

  const fetchCitations = async () => {
    try {
      const [citRes, citedByRes] = await Promise.all([
        axios.get(`/api/v1/cases/${caseId}/citations`),
        axios.get(`/api/v1/cases/${caseId}/cited-by`)
      ]);
      setCitations([...citRes.data.resolved, ...citRes.data.unresolved]);
      setCitedBy(citedByRes.data);
    } catch (err) {
      console.error('Error fetching citations', err);
    }
  };

  const generateSummary = async () => {
    setIsLoadingSummary(true);
    setError('');
    try {
      const res = await axios.post(`/api/v1/cases/${caseId}/summarize`);
      setSummary(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
    } finally {
      setIsLoadingSummary(false);
    }
  };

  const extractPrinciples = async () => {
    setIsLoadingPrinciples(true);
    setError('');
    try {
      const res = await axios.post(`/api/v1/cases/${caseId}/principles/extract`);
      setPrinciples(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to extract principles');
    } finally {
      setIsLoadingPrinciples(false);
    }
  };

  const findSimilarCases = async () => {
    setIsLoadingSimilar(true);
    setError('');
    try {
      const res = await axios.get(`/api/v1/cases/${caseId}/similar?limit=5`);
      setSimilarCases(res.data.similar_cases || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to find similar cases');
    } finally {
      setIsLoadingSimilar(false);
    }
  };

  const extractCitations = async () => {
    setIsLoadingCitations(true);
    setError('');
    try {
      await axios.post(`/api/v1/cases/${caseId}/citations/extract`);
      fetchCitations();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to extract citations');
    } finally {
      setIsLoadingCitations(false);
    }
  };

  const handleSourceClick = async (chunkId) => {
    setLoadingSourceId(chunkId);
    try {
      const res = await axios.get(`/api/v1/citations/${chunkId}`);
      if (onViewSource) {
        onViewSource({
          documentId: res.data.document_id,
          pageNumber: res.data.page_number,
          content: res.data.content,
          documentName: res.data.document_name
        });
      }
    } catch (err) {
      console.error("Failed to load source", err);
      alert("Failed to load source passage.");
    } finally {
      setLoadingSourceId(null);
    }
  };

  if (!caseId) return null;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BookOpen },
    { id: 'principles', label: 'Principles', icon: Scale },
    { id: 'similar', label: 'Similar Cases', icon: Search },
    { id: 'citations', label: 'Citations', icon: Network },
  ];

  return (
    <div className="w-full flex flex-col">
      {/* Case Header */}
      <div className="mb-6">
        <h2 className="font-serif font-medium text-2xl text-foreground mb-2">
          {summary?.case_title || 'Case Analysis'}
        </h2>
        {summary && (
          <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted">
            <span>{summary.court}</span>
            <span>&bull;</span>
            <span>{summary.judgment_date}</span>
            <span>&bull;</span>
            <span>{summary.case_number}</span>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md border border-destructive/20 font-medium">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex space-x-1 border-b border-border mb-6">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors duration-200 border-b-2 ${
              activeTab === tab.id 
                ? 'border-primary text-primary' 
                : 'border-transparent text-muted hover:text-foreground hover:border-border'
            }`}
          >
            <tab.icon size={16} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 bg-surface rounded-md">
        
        {/* OVERVIEW TAB */}
        {activeTab === 'overview' && (
          <div className="animate-in fade-in duration-300">
            {summary ? (
              <div className="flex flex-col gap-8">
                <div>
                  <h3 className="font-serif font-medium text-lg text-foreground mb-3 border-b border-border pb-2">Executive Summary</h3>
                  <p className="text-foreground leading-relaxed text-[15px]">{summary.executive_summary}</p>
                </div>
                <div>
                  <h3 className="font-serif font-medium text-lg text-foreground mb-3 border-b border-border pb-2">Issues</h3>
                  <ul className="list-disc pl-5 space-y-2 text-foreground leading-relaxed text-[15px]">
                    {summary.issues?.map((issue, i) => <li key={i}>{issue}</li>)}
                  </ul>
                </div>
                <div>
                  <h3 className="font-serif font-medium text-lg text-foreground mb-3 border-b border-border pb-2">Final Decision</h3>
                  <p className="text-foreground leading-relaxed text-[15px]">{summary.final_decision}</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-md bg-muted/10">
                <FileText size={24} className="text-muted mb-4" />
                <h3 className="font-sans font-medium text-lg text-foreground">Analysis Required</h3>
                <p className="text-sm text-muted mt-2 max-w-sm">Generate an AI summary to extract the executive summary, issues, and final decision.</p>
                <button
                  onClick={generateSummary}
                  disabled={isLoadingSummary}
                  className="mt-6 flex items-center gap-2 px-5 py-2.5 bg-foreground text-white rounded-md hover:bg-primary transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {isLoadingSummary ? <Loader2 className="animate-spin" size={16} /> : <FileText size={16} />}
                  Generate Overview
                </button>
              </div>
            )}
          </div>
        )}

        {/* PRINCIPLES TAB */}
        {activeTab === 'principles' && (
          <div className="animate-in fade-in duration-300">
            {principles && principles.length > 0 ? (
              <div className="flex flex-col gap-6">
                {principles.map((p, idx) => (
                  <div key={p.id || idx} className="pb-6 border-b border-border last:border-0 last:pb-0">
                    <h4 className="font-serif font-medium text-lg text-foreground mb-2">{p.principle_title}</h4>
                    <p className="text-foreground leading-relaxed text-[15px] mb-3">{p.principle_text}</p>
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-medium text-muted uppercase tracking-wider">
                        Confidence: {(p.confidence_score * 100).toFixed(0)}%
                      </span>
                      {p.supporting_chunk_id && (
                        <>
                          <span className="text-border">&bull;</span>
                          <button 
                            onClick={() => handleSourceClick(p.supporting_chunk_id)}
                            disabled={loadingSourceId === p.id}
                            className="text-xs font-medium text-primary hover:text-foreground flex items-center gap-1 transition-colors disabled:opacity-50"
                          >
                            {loadingSourceId === p.id ? <Loader2 size={12} className="animate-spin"/> : <ExternalLink size={12}/>}
                            View Source Evidence
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : principles !== null && principles.length === 0 ? (
              <div className="p-6 text-center text-sm text-muted bg-muted/10 rounded-md">
                No legal principles were extracted from this case.
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-md bg-muted/10">
                <Scale size={24} className="text-muted mb-4" />
                <h3 className="font-sans font-medium text-lg text-foreground">Extract Principles</h3>
                <p className="text-sm text-muted mt-2 max-w-sm">Use AI to extract the core legal doctrines and rules established in this judgment.</p>
                <button
                  onClick={extractPrinciples}
                  disabled={isLoadingPrinciples}
                  className="mt-6 flex items-center gap-2 px-5 py-2.5 bg-foreground text-white rounded-md hover:bg-primary transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {isLoadingPrinciples ? <Loader2 className="animate-spin" size={16} /> : <List size={16} />}
                  Extract Principles
                </button>
              </div>
            )}
          </div>
        )}

        {/* SIMILAR CASES TAB */}
        {activeTab === 'similar' && (
          <div className="animate-in fade-in duration-300">
            {similarCases && similarCases.length > 0 ? (
              <div className="flex flex-col gap-6">
                {similarCases.map((sc, idx) => (
                  <div key={sc.case_id || idx} className="p-5 border border-border rounded-md bg-surface hover:border-primary/30 transition-colors">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h4 className="font-serif font-medium text-lg text-foreground cursor-pointer hover:text-primary transition-colors" onClick={() => onCaseSelect && onCaseSelect(sc.case_id)}>
                          {sc.case_title}
                        </h4>
                        <div className="text-xs text-muted mt-1 flex gap-2">
                          <span>{sc.court}</span>
                          <span>&bull;</span>
                          <span>{sc.judgment_date}</span>
                        </div>
                      </div>
                      <div className="text-xs font-medium text-muted uppercase tracking-wider">
                        Score: {sc.similarity_score}
                      </div>
                    </div>
                    
                    {sc.matched_chunks && sc.matched_chunks.length > 0 && (
                      <div className="my-4 pl-4 border-l-2 border-primary/20">
                        <p className="text-sm text-foreground/80 font-serif italic">"{sc.matched_chunks[0].excerpt}"</p>
                      </div>
                    )}
                    
                    <div className="flex gap-4">
                      {sc.matched_chunks && sc.matched_chunks.length > 0 && (
                        <button 
                          onClick={() => handleSourceClick(sc.matched_chunks[0].chunk_id)}
                          disabled={loadingSourceId === sc.matched_chunks[0].chunk_id}
                          className="text-xs font-medium text-primary hover:text-foreground flex items-center gap-1 transition-colors disabled:opacity-50"
                        >
                          {loadingSourceId === sc.matched_chunks[0].chunk_id ? <Loader2 size={12} className="animate-spin"/> : <ExternalLink size={12}/>}
                          View Source Evidence
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : similarCases !== null && similarCases.length === 0 ? (
              <div className="p-6 text-center text-sm text-muted bg-muted/10 rounded-md">
                No sufficiently similar cases found in the database.
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-md bg-muted/10">
                <Search size={24} className="text-muted mb-4" />
                <h3 className="font-sans font-medium text-lg text-foreground">Semantic Search</h3>
                <p className="text-sm text-muted mt-2 max-w-sm">Find related case law using L2 distance search across the vector database.</p>
                <button
                  onClick={findSimilarCases}
                  disabled={isLoadingSimilar}
                  className="mt-6 flex items-center gap-2 px-5 py-2.5 bg-foreground text-white rounded-md hover:bg-primary transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {isLoadingSimilar ? <Loader2 className="animate-spin" size={16} /> : <Search size={16} />}
                  Find Similar Cases
                </button>
              </div>
            )}
          </div>
        )}

        {/* CITATIONS TAB */}
        {activeTab === 'citations' && (
          <div className="animate-in fade-in duration-300">
            {citations.length > 0 || citedBy.length > 0 ? (
              <div className="flex flex-col gap-6">
                <div className="border border-border rounded-md overflow-hidden bg-surface">
                  <CitationNetworkGraph
                    currentCase={summary ? { id: caseId, title: summary.case_title } : { id: caseId, title: 'Current Case' }}
                    citations={citations}
                    citedBy={citedBy}
                    onNodeClick={(id) => onCaseSelect && onCaseSelect(id)}
                    onEdgeClick={(citationId) => {
                      const cit = [...citations, ...citedBy].find(c => c.id === citationId);
                      if (cit && cit.source_chunk_id) {
                         handleSourceClick(cit.source_chunk_id);
                      }
                    }}
                  />
                </div>
                
                {citations.filter(c => !c.target_case_id).length > 0 && (
                  <div className="p-4 bg-muted/10 border border-border rounded-md">
                    <h4 className="text-sm font-medium text-foreground mb-3 uppercase tracking-wider">Unresolved Citations</h4>
                    <ul className="text-sm text-muted space-y-2">
                      {citations.filter(c => !c.target_case_id).map((c, idx) => (
                        <li key={c.id || idx} className="pl-4 border-l-2 border-border">
                          <span className="font-medium text-foreground">{c.target_case_title}</span> <br/>
                          <span className="italic font-serif">"{c.citation_text}"</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-border rounded-md bg-muted/10">
                <Network size={24} className="text-muted mb-4" />
                <h3 className="font-sans font-medium text-lg text-foreground">Citation Network</h3>
                <p className="text-sm text-muted mt-2 max-w-sm">Extract all citations and build a visual network of preceding and subsequent case law.</p>
                <button
                  onClick={extractCitations}
                  disabled={isLoadingCitations}
                  className="mt-6 flex items-center gap-2 px-5 py-2.5 bg-foreground text-white rounded-md hover:bg-primary transition-colors text-sm font-medium disabled:opacity-50"
                >
                  {isLoadingCitations ? <Loader2 className="animate-spin" size={16} /> : <Network size={16} />}
                  Extract Citations
                </button>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
};

export default CaseView;
