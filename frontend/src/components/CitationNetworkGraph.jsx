import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const CitationNetworkGraph = ({ currentCase, citations, citedBy, onNodeClick, onEdgeClick }) => {
  const graphRef = useRef(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [dimensions, setDimensions] = useState({ width: 0, height: 500 });
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.offsetWidth,
        height: 500
      });
    }

    const handleResize = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: 500
        });
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!currentCase) return;

    const nodes = [];
    const links = [];

    nodes.push({
      id: currentCase.id,
      name: currentCase.title,
      type: 'current',
      val: 20
    });

    citations.forEach(cit => {
      if (cit.target_case_id) {
        if (!nodes.find(n => n.id === cit.target_case_id)) {
          nodes.push({
            id: cit.target_case_id,
            name: cit.target_case_title,
            type: 'cited',
            val: 10
          });
        }
        
        links.push({
          source: currentCase.id,
          target: cit.target_case_id,
          relationship: cit.relationship_type || 'cited',
          citationId: cit.id
        });
      }
    });

    citedBy.forEach(cit => {
      if (cit.source_case_id) {
        if (!nodes.find(n => n.id === cit.source_case_id)) {
          nodes.push({
            id: cit.source_case_id,
            name: cit.source_case_title,
            type: 'cited_by',
            val: 10
          });
        }

        links.push({
          source: cit.source_case_id,
          target: currentCase.id,
          relationship: cit.relationship_type || 'cited',
          citationId: cit.id
        });
      }
    });

    setGraphData({ nodes, links });

  }, [currentCase, citations, citedBy]);

  useEffect(() => {
    if (graphRef.current && graphData.nodes.length > 0) {
      graphRef.current.d3Force('charge').strength(-400);
      setTimeout(() => {
        if (graphRef.current) {
          graphRef.current.zoomToFit(400, 50);
        }
      }, 500);
    }
  }, [graphData]);

  if (!graphData.nodes.length || graphData.nodes.length === 1) {
    const totalFound = citations.length;
    const resolvedFound = citations.filter(c => c.target_case_id).length;
    
    return (
      <div className="flex flex-col items-center justify-center h-64 bg-surface rounded-md text-center">
        <p className="text-muted text-sm font-medium mb-2">No resolved citation relationships are available yet.</p>
        {totalFound > 0 && (
          <p className="text-xs text-muted/70">
            {totalFound} citations were found in this judgment,<br/>
            but {totalFound - resolvedFound} are not currently indexed in Lexis AI.
          </p>
        )}
      </div>
    );
  }

  const getNodeColor = (node) => {
    if (node.type === 'current') return '#1e293b'; // foreground / dark navy
    if (node.type === 'cited') return '#64748b'; // slate
    if (node.type === 'cited_by') return '#94a3b8'; // lighter slate
    return '#cbd5e1';
  };

  return (
    <div ref={containerRef} className="w-full bg-background relative border-b border-border">
      <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 text-[11px] font-medium uppercase tracking-wider bg-surface/80 p-3 rounded backdrop-blur-md border border-border">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#1e293b]"></span>
          <span className="text-foreground">Current Case</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#64748b]"></span>
          <span className="text-foreground">Cited Cases (Outbound)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#94a3b8]"></span>
          <span className="text-foreground">Cited By (Inbound)</span>
        </div>
      </div>
      
      {dimensions.width > 0 && (
        <ForceGraph2D
          ref={graphRef}
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeLabel="name"
          nodeColor={getNodeColor}
          nodeRelSize={1.5}
          linkColor={() => '#e2e8f0'} // very light gray
          linkWidth={1.5}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          onNodeClick={(node) => {
            if (node.id !== currentCase.id && onNodeClick) {
              onNodeClick(node.id);
            }
          }}
          onLinkClick={(link) => {
            if (onEdgeClick) {
              onEdgeClick(link.citationId);
            }
          }}
          linkLabel="relationship"
          linkHoverPrecision={10}
          backgroundColor="transparent"
          linkCanvasObjectMode={() => 'after'}
          linkCanvasObject={(link, ctx, globalScale) => {
            const MAX_FONT_SIZE = 3.5;
            const LABEL_NODE_MARGIN = graphRef.current ? graphRef.current.d3Force('link').distance() * 0.1 : 15;

            const start = link.source;
            const end = link.target;

            if (typeof start !== 'object' || typeof end !== 'object') return;

            const textPos = Object.assign(...['x', 'y'].map(c => ({
              [c]: start[c] + (end[c] - start[c]) / 2
            })));

            const relLink = { x: end.x - start.x, y: end.y - start.y };
            const maxTextLength = Math.sqrt(Math.pow(relLink.x, 2) + Math.pow(relLink.y, 2)) - LABEL_NODE_MARGIN * 2;

            let textAngle = Math.atan2(relLink.y, relLink.x);
            if (textAngle > Math.PI / 2) textAngle = -(Math.PI - textAngle);
            if (textAngle < -Math.PI / 2) textAngle = -(Math.PI + textAngle);

            const label = link.relationship;

            ctx.font = '1px Sans-Serif';
            const fontSize = Math.min(MAX_FONT_SIZE, maxTextLength / ctx.measureText(label).width);
            ctx.font = `${fontSize}px Sans-Serif`;
            const textWidth = ctx.measureText(label).width;
            const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

            ctx.save();
            ctx.translate(textPos.x, textPos.y);
            ctx.rotate(textAngle);

            ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
            ctx.fillRect(- bckgDimensions[0] / 2, - bckgDimensions[1] / 2, ...bckgDimensions);

            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#64748b'; // slate-500
            ctx.fillText(label, 0, 0);
            ctx.restore();
          }}
        />
      )}
    </div>
  );
};

export default CitationNetworkGraph;
