import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import axios from 'axios';
import { FiArrowLeft, FiAlertTriangle, FiCheckCircle, FiFile, FiMessageCircle } from 'react-icons/fi';

const ClaimDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [userRole, setUserRole] = useState(null);

  const fetchClaimDetails = useCallback(async () => {
    try {
      const response = await axios.get(`http://localhost:8000/claims/${id}`);
      setClaim(response.data);
    } catch (error) {
      console.error('Failed to fetch claim details:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    setUserRole(user.role);
    fetchClaimDetails();
  }, [fetchClaimDetails]);

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMessage = { role: 'user', content: chatMessage };
    setChatHistory([...chatHistory, userMessage]);
    setChatMessage('');

    try {
      const response = await axios.post('http://localhost:8000/rag_chat', {
        query: chatMessage
      });

      const botMessage = { 
        role: 'assistant', 
        content: response.data.answer || 'No answer available.'
      };
      setChatHistory(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.'
      };
      setChatHistory(prev => [...prev, errorMessage]);
    }
  };


  const handleApprove = async () => {
  try {
    await axios.post(`http://localhost:8000/claims/decision?doc_id=${id}&decision=approved&note=Approved by agent`);
    alert('Claim approved successfully!');
    fetchClaimDetails();
  } catch (error) {
    console.error('Failed to approve:', error);
    alert('Failed to update status');
  }
};

const handleReject = async () => {
  try {
    await axios.post(`http://localhost:8000/claims/decision?doc_id=${id}&decision=rejected&note=Rejected by agent`);
    alert('Claim rejected successfully!');
    fetchClaimDetails();
  } catch (error) {
    console.error('Failed to reject:', error);
    alert('Failed to update status');
  }
};


  if (loading) {
    return (
      <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
          <p>Loading claim details...</p>
        </div>
      </div>
    );
  }

  if (!claim) {
    return (
      <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
        <Navbar />
        <div className="container" style={{ paddingTop: '40px', textAlign: 'center' }}>
          <p>Claim not found</p>
        </div>
      </div>
    );
  }

  const fraudScore = claim.tamper_score || 0;
  const fraudLevel = fraudScore > 0.7 ? 'HIGH' : fraudScore > 0.4 ? 'MEDIUM' : 'LOW';
  const fraudColor = fraudScore > 0.7 ? '#EF4444' : fraudScore > 0.4 ? '#F59E0B' : '#10B981';

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
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontWeight: '500',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          <FiArrowLeft /> Back
        </button>

        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '24px',
          marginTop: '8px'
        }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: '700',
            color: '#1E3A8A',
            margin: 0
          }}>
            Claim Details
          </h1>

          <button
            onClick={() => navigate(`/shap/${id}`)}
            style={{
              background: '#8B5CF6',
              color: 'white',
              padding: '10px 18px',
              borderRadius: '8px',
              border: 'none',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <FiMessageCircle size={18} />
            View SHAP Explainability
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
          <div>
            {/* Main Claim Info */}
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#1E3A8A' }}>
                  Claim #{String(claim.id).padStart(4, '0')}
                </h2>
                <span className={`badge badge-${claim.status || claim.agent_decision || 'pending'}`}>
                  {claim.status || claim.agent_decision || 'processed'}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <p style={{ color: '#6B7280', marginBottom: '5px' }}>Submitted By</p>
                  <p style={{ fontWeight: '600', color: '#1E3A8A' }}>
                    {claim.filename ? claim.filename.split('.')[0].replace(/doc_\d+_/, '') : 'Anonymous'}
                  </p>
                </div>
                <div>
                  <p style={{ color: '#6B7280', marginBottom: '5px' }}>Submitted On</p>
                  <p style={{ fontWeight: '600', color: '#1E3A8A' }}>
                    {new Date().toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </p>
                </div>
                <div>
                  <p style={{ color: '#6B7280', marginBottom: '5px' }}>Claim Type</p>
                  <p style={{ fontWeight: '600', color: '#1E3A8A', textTransform: 'capitalize' }}>
                    Document
                  </p>
                </div>
                <div>
                  <p style={{ color: '#6B7280', marginBottom: '5px' }}>Document</p>
                  <a
                    href={`http://localhost:8000/view_document/${id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      color: '#5DCCF5',
                      fontWeight: '600',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                  >
                    <FiFile /> View Document
                  </a>
                </div>
              </div>
            </div>
          </div>


            {/* Fraud Analysis */}
            <div className="card">
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#1E3A8A',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <FiAlertTriangle color={fraudColor} /> Fraud Analysis
              </h2>

              <div style={{
                background: '#F9FAFB',
                padding: '20px',
                borderRadius: '8px',
                marginBottom: '20px'
              }}>
                <div style={{ marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span style={{ fontWeight: '600', color: '#1E3A8A' }}>Fraud Score</span>
                    <span style={{ fontWeight: '700', color: fraudColor, fontSize: '18px' }}>
                      {(fraudScore * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div style={{
                    width: '100%',
                    height: '12px',
                    background: '#E5E7EB',
                    borderRadius: '6px',
                    overflow: 'hidden'
                  }}>
                    <div style={{
                      width: `${fraudScore * 100}%`,
                      height: '100%',
                      background: fraudColor,
                      transition: 'width 0.3s ease'
                    }} />
                  </div>
                </div>
                <div style={{
                  marginTop: '15px',
                  padding: '12px',
                  background: fraudLevel === 'HIGH' ? '#FEE2E2' : fraudLevel === 'MEDIUM' ? '#FEF3C7' : '#D1FAE5',
                  borderRadius: '6px',
                  textAlign: 'center'
                }}>
                  <span style={{
                    fontWeight: '700',
                    color: fraudLevel === 'HIGH' ? '#991B1B' : fraudLevel === 'MEDIUM' ? '#92400E' : '#065F46',
                    fontSize: '16px'
                  }}>
                    {fraudLevel} RISK
                  </span>
                </div>
              </div>
            </div>

            {/* RAG Chatbot */}
            <div className="card">
              <h2 style={{
                fontSize: '20px',
                fontWeight: '600',
                color: '#1E3A8A',
                marginBottom: '20px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <FiMessageCircle /> Ask Questions
              </h2>

              <div style={{
                background: '#F9FAFB',
                padding: '15px',
                borderRadius: '8px',
                height: '300px',
                overflowY: 'auto',
                marginBottom: '15px'
              }}>
                {chatHistory.length === 0 ? (
                  <p style={{ color: '#6B7280', textAlign: 'center', padding: '20px' }}>
                    Ask questions about this claim or policy details
                  </p>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: msg.role === 'user' ? '#E0F2FE' : 'white',
                        padding: '12px',
                        borderRadius: '8px',
                        marginBottom: '10px',
                        marginLeft: msg.role === 'user' ? '20px' : '0',
                        marginRight: msg.role === 'user' ? '0' : '20px'
                      }}
                    >
                      <p style={{
                        fontSize: '12px',
                        fontWeight: '600',
                        color: '#6B7280',
                        marginBottom: '5px'
                      }}>
                        {msg.role === 'user' ? 'You' : 'Assistant'}
                      </p>
                      <p style={{ color: '#1E3A8A' }}>{msg.content}</p>
                    </div>
                  ))
                )}
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Type your question..."
                  style={{
                    flex: 1,
                    padding: '12px',
                    borderRadius: '8px',
                    border: '2px solid #E5E7EB',
                    fontSize: '16px'
                  }}
                />
                <button
                  onClick={sendChatMessage}
                  style={{
                    background: '#5DCCF5',
                    color: 'white',
                    padding: '12px 24px',
                    borderRadius: '8px',
                    fontWeight: '600',
                    border: 'none',
                    cursor: 'pointer'
                  }}
                >
                  Send
                </button>
              </div>
            </div>
          </div>

          {/*Agent Sidebar */}
          <div>
            {userRole === 'agent' && (
              <div className="card">
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#1E3A8A',
                  marginBottom: '15px'
                }}>
                  Quick Actions
                </h3>
                {/* Only show buttons if NOT already approved or rejected */}
    {(!claim.agent_decision || claim.agent_decision === 'pending' || claim.agent_decision === 'processed') ? (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <button
          onClick={handleApprove}
          style={{
            background: '#D1FAE5',
            color: '#065F46',
            padding: '12px',
            borderRadius: '8px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          <FiCheckCircle /> Approve Claim
        </button>
        <button
          onClick={handleReject}
          style={{
            background: '#FEE2E2',
            color: '#991B1B',
            padding: '12px',
            borderRadius: '8px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          <FiAlertTriangle /> Reject Claim
        </button>
      </div>
    ) : (
      <div style={{
        padding: '20px',
        textAlign: 'center',
        background: claim.agent_decision === 'approved' ? '#D1FAE5' : '#FEE2E2',
        color: claim.agent_decision === 'approved' ? '#065F46' : '#991B1B',
        borderRadius: '8px',
        fontWeight: '600'
      }}>
        {claim.agent_decision === 'approved' ? '✓ Claim Approved' : '✗ Claim Rejected'}
      </div>
    )}
  </div>
)}
            <div className="card">
              <h3 style={{
                fontSize: '18px',
                fontWeight: '600',
                color: '#1E3A8A',
                marginBottom: '15px'
              }}>
                Detection Indicators
              </h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                <li style={{ padding: '8px 0', borderBottom: '1px solid #E5E7EB' }}>
                  <span style={{ color: '#6B7280' }}>Document Authenticity:</span>
                  <strong style={{ float: 'right', color: fraudColor }}>
                    {fraudScore < 0.3 ? 'Verified' : 'Suspicious'}
                  </strong>
                </li>
                <li style={{ padding: '8px 0', borderBottom: '1px solid #E5E7EB' }}>
                  <span style={{ color: '#6B7280' }}>Tamper Detection:</span>
                  <strong style={{ float: 'right', color: fraudColor }}>
                    {fraudScore < 0.5 ? 'Clean' : 'Detected'}
                  </strong>
                </li>
                <li style={{ padding: '8px 0' }}>
                  <span style={{ color: '#6B7280' }}>Risk Level:</span>
                  <strong style={{ float: 'right', color: fraudColor }}>
                    {fraudLevel}
                  </strong>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
  );
};

export default ClaimDetails;

