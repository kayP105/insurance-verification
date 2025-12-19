import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import Navbar from './components/Navbar';

function ShapExplainer() {
  const { claimId } = useParams(); // Get claimId from URL
  const navigate = useNavigate();
  const [shapData, setShapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (claimId) {
      fetchShapData();
    }
  }, [claimId]);

  const fetchShapData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/shap_explain/${claimId}`);
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setShapData(data);
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch SHAP explanation');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
          <p>Loading SHAP explanation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
          <p style={{ color: '#EF4444' }}>{error}</p>
          <button onClick={() => navigate(-1)} style={{ marginTop: '20px' }}>
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!shapData) {
    return (
      <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
          <p>No SHAP data available</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
      <Navbar />
      <div className="container" style={{ paddingTop: '40px', paddingBottom: '40px' }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            background: 'white',
            color: '#1E3A8A',
            padding: '10px 20px',
            borderRadius: '8px',
            marginBottom: '20px',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          ← Back
        </button>

        <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#1E3A8A', marginBottom: '30px' }}>
          SHAP Explainability for Claim #{claimId}
        </h1>

        <div className="card" style={{ marginBottom: '20px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1E3A8A', marginBottom: '15px' }}>
            Model Explanation
          </h2>
          <p style={{ color: '#6B7280', marginBottom: '10px' }}>
            <strong>Base Prediction Value:</strong> {shapData.base_value?.toFixed(4)}
          </p>
        </div>

        {shapData.features && shapData.features.length > 0 && (
          <div className="card">
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1E3A8A', marginBottom: '15px' }}>
              Feature Contributions
            </h2>
            
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={shapData.features}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="feature" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="shap_value" fill="#8884d8">
                  {shapData.features.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.shap_value > 0 ? '#ff6b6b' : '#4ecdc4'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>

            <table style={{ width: '100%', marginTop: '20px', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#F9FAFB' }}>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #E5E7EB' }}>Feature</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #E5E7EB' }}>Value</th>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #E5E7EB' }}>SHAP Impact</th>
                </tr>
              </thead>
              <tbody>
                {shapData.features.map((feat, idx) => (
                  <tr key={idx}>
                    <td style={{ padding: '12px', borderBottom: '1px solid #E5E7EB' }}>{feat.feature}</td>
                    <td style={{ padding: '12px', borderBottom: '1px solid #E5E7EB' }}>{feat.value}</td>
                    <td style={{
                      padding: '12px',
                      borderBottom: '1px solid #E5E7EB',
                      color: feat.shap_value > 0 ? '#ff6b6b' : '#4ecdc4',
                      fontWeight: 'bold'
                    }}>
                      {feat.shap_value.toFixed(4)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default ShapExplainer;
