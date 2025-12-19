import React, { useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

function FraudGraph() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      const response = await fetch('http://localhost:8000/fraud_graph');
      const data = await response.json();
      
      // Transform the data to match react-force-graph format
      const formattedData = {
        nodes: data.nodes.map(node => ({
          id: node.id,
          name: node.label || node.id,
          type: node.type || 'document',
          ...node
        })),
        links: data.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          label: edge.relationship || '',
          ...edge
        }))
      };
      
      setGraphData(formattedData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching fraud graph:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading fraud graph...</div>;

  return (
    <div style={{ width: '100%', height: '600px' }}>
      <h2>Fraud Detection Network Graph</h2>
      <ForceGraph2D
        graphData={graphData}
        nodeLabel="name"
        nodeAutoColorBy="type"
        linkLabel="label"
        linkDirectionalArrowLength={3.5}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0.25}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = node.name;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          
          // Draw circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, 5, 0, 2 * Math.PI, false);
          ctx.fillStyle = node.type === 'policy' ? '#ff6b6b' : '#4ecdc4';
          ctx.fill();
          
          // Draw label
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = '#333';
          ctx.fillText(label, node.x, node.y + 10);
        }}
      />
    </div>
  );
}

export default FraudGraph;
