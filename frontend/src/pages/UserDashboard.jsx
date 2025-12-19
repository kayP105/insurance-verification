import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import axios from 'axios';
import { 
  FiUpload, FiFile, FiClock, FiCheckCircle, FiXCircle, 
  FiAlertCircle,  FiFileText, 
} from 'react-icons/fi';

const UserDashboard = () => {
  const [claims, setClaims] = useState([]);
  const [file, setFile] = useState(null);
  const [claimType, setClaimType] = useState('health');
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      const response = await axios.get('http://localhost:8000/claims');
      const claimsData = response.data.claims || [];
      
      if (Array.isArray(claimsData)) {
        setClaims(claimsData);
      } else {
        console.error('Claims data is not an array:', claimsData);
        setClaims([]);
      }
    } catch (error) {
      console.error('Failed to fetch claims:', error);
      setClaims([]);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('claim_type', claimType);

    try {
      await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setFile(null);
      setClaimType('health');
      fetchClaims();
      alert('Claim uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + (error.response?.data?.detail || error.message || 'Unknown error'));
    } finally {
      setUploading(false);
    }
  };

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
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = { type: 'user', text: chatInput };
    setChatMessages([...chatMessages, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/rag_chat', {
        query: chatInput
      });
      
      const botMessage = { type: 'bot', text: response.data.answer };
      setChatMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = { type: 'bot', text: 'Sorry, I encountered an error. Please try again.' };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch(status) {
      case 'approved': return <FiCheckCircle color="#10B981" size={20} />;
      case 'rejected': return <FiXCircle color="#EF4444" size={20} />;
      case 'pending': return <FiClock color="#F59E0B" size={20} />;
      default: return <FiAlertCircle color="#6B7280" size={20} />;
    }
  };

  // Calculate stats with safety checks
  const stats = {
    total: Array.isArray(claims) ? claims.length : 0,
    pending: Array.isArray(claims) ? claims.filter(c => c.agent_decision === 'pending' || !c.agent_decision).length : 0,
    approved: Array.isArray(claims) ? claims.filter(c => c.agent_decision === 'approved').length : 0,
    rejected: Array.isArray(claims) ? claims.filter(c => c.agent_decision === 'rejected').length : 0
  };

  return (
    <div style={{ background: '#F9FAFB', minHeight: '100vh' }}>
      <Navbar />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
        
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            My Claims Dashboard
          </h1>
          <p style={{ color: '#6B7280', fontSize: '14px' }}>
            Submit and track your insurance claims
          </p>
        </div>

        {/* Stats Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '32px' }}>
          <StatCard 
            title="Total Claims" 
            value={stats.total} 
            icon={FiFileText} 
            color="#3B82F6"
            bgColor="#EFF6FF"
          />
          <StatCard 
            title="Pending" 
            value={stats.pending} 
            icon={FiClock} 
            color="#F59E0B"
            bgColor="#FEF3C7"
          />
          <StatCard 
            title="Approved" 
            value={stats.approved} 
            icon={FiCheckCircle} 
            color="#10B981"
            bgColor="#D1FAE5"
          />
          <StatCard 
            title="Rejected" 
            value={stats.rejected} 
            icon={FiXCircle} 
            color="#EF4444"
            bgColor="#FEE2E2"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '24px' }}>
          
          {/* Upload Section */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            border: '1px solid #E5E7EB',
            height: 'fit-content'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                Submit New Claim
              </h3>
              <p style={{ fontSize: '13px', color: '#6B7280' }}>Upload your claim document</p>
            </div>

            <form onSubmit={handleFileUpload}>
              {/* Claim Type Selector */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>
                  Claim Type
                </label>
                <select
                  value={claimType}
                  onChange={(e) => setClaimType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: '1px solid #D1D5DB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    background: 'white',
                    cursor: 'pointer'
                  }}
                >
                  <option value="health">Health Insurance</option>
                  <option value="auto">Auto Insurance</option>
                  <option value="home">Home Insurance</option>
                  <option value="life">Life Insurance</option>
                </select>
              </div>

              {/* File Upload Area */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                style={{
                  border: dragActive ? '2px dashed #3B82F6' : '2px dashed #D1D5DB',
                  borderRadius: '12px',
                  padding: '32px',
                  textAlign: 'center',
                  background: dragActive ? '#EFF6FF' : '#F9FAFB',
                  marginBottom: '20px',
                  transition: 'all 0.3s',
                  cursor: 'pointer'
                }}
              >
                <input
                  type="file"
                  id="file-upload"
                  onChange={(e) => setFile(e.target.files[0])}
                  style={{ display: 'none' }}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
                <label htmlFor="file-upload" style={{ cursor: 'pointer' }}>
                  <FiUpload size={40} color={dragActive ? '#3B82F6' : '#9CA3AF'} style={{ margin: '0 auto 12px' }} />
                  <p style={{ color: '#374151', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
                    {file ? file.name : 'Click to upload or drag and drop'}
                  </p>
                  <p style={{ color: '#9CA3AF', fontSize: '12px' }}>
                    PDF, PNG, JPG (MAX. 10MB)
                  </p>
                </label>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!file || uploading}
                style={{
                  width: '100%',
                  background: !file || uploading ? '#D1D5DB' : '#3B82F6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '14px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: !file || uploading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                {uploading ? (
                  <>
                    <div style={{
                      width: '16px',
                      height: '16px',
                      border: '2px solid white',
                      borderTopColor: 'transparent',
                      borderRadius: '50%',
                      animation: 'spin 1s linear infinite'
                    }} />
                    Processing...
                  </>
                ) : (
                  <>
                    <FiUpload size={18} />
                    Submit Claim
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Claims List */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            border: '1px solid #E5E7EB'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                Recent Claims
              </h3>
              <p style={{ fontSize: '13px', color: '#6B7280' }}>Track your claim submissions</p>
            </div>

            {!Array.isArray(claims) || claims.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                <FiFile size={48} color="#D1D5DB" style={{ margin: '0 auto 16px' }} />
                <p style={{ color: '#9CA3AF', fontSize: '14px', marginBottom: '4px' }}>No claims yet</p>
                <p style={{ color: '#D1D5DB', fontSize: '13px' }}>Submit your first claim to get started</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {claims.map((claim) => {
                  const fraudScore = ((claim.tamper_score || 0) * 100).toFixed(1);
                  const fraudColor = (claim.tamper_score || 0) > 0.7 ? '#EF4444' : (claim.tamper_score || 0) > 0.4 ? '#F59E0B' : '#10B981';
                  const status = claim.agent_decision || claim.status || 'pending';
                  
                  return (
                    <div
                      key={claim.id}
                      onClick={() => navigate(`/claim/${claim.id}`)}
                      style={{
                        background: '#F9FAFB',
                        border: '1px solid #E5E7EB',
                        borderRadius: '12px',
                        padding: '16px',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';
                        e.currentTarget.style.transform = 'translateY(-2px)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.boxShadow = 'none';
                        e.currentTarget.style.transform = 'translateY(0)';
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                            <span style={{ fontFamily: 'monospace', fontSize: '14px', fontWeight: '600', color: '#3B82F6' }}>
                              #{String(claim.id).padStart(4, '0')}
                            </span>
                            <span style={{
                              background: '#EFF6FF',
                              color: '#3B82F6',
                              padding: '2px 8px',
                              borderRadius: '8px',
                              fontSize: '12px',
                              fontWeight: '500',
                              textTransform: 'capitalize'
                            }}>
                              {claim.filename || 'Document'}
                            </span>
                          </div>
                          <p style={{ fontSize: '13px', color: '#6B7280' }}>
                            {new Date().toLocaleDateString('en-US', { 
                              month: 'long', 
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </p>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {getStatusIcon(status)}
                          <span style={{
                            fontSize: '13px',
                            fontWeight: '600',
                            color: status === 'approved' ? '#10B981' : 
                                   status === 'rejected' ? '#EF4444' : '#F59E0B',
                            textTransform: 'capitalize'
                          }}>
                            {status}
                          </span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <p style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '4px' }}>Fraud Risk Score</p>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{
                              width: '80px',
                              height: '6px',
                              background: '#E5E7EB',
                              borderRadius: '3px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${fraudScore}%`,
                                height: '100%',
                                background: fraudColor,
                                borderRadius: '3px'
                              }} />
                            </div>
                            <span style={{ color: fraudColor, fontWeight: '600', fontSize: '13px' }}>
                              {fraudScore}%
                            </span>
                          </div>
                        </div>
                        <button style={{
                          background: '#3B82F6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '8px 16px',
                          fontSize: '13px',
                          fontWeight: '500',
                          cursor: 'pointer'
                        }}>
                          View Details
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* RAG Chatbot Widget */}
      <div style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 1000
      }}>
        {/* Chat Button */}
        {!chatOpen && (
          <button
            onClick={() => setChatOpen(true)}
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px'
            }}
          >
            💬
          </button>
        )}

        {/* Chat Window */}
        {chatOpen && (
          <div style={{
            width: '380px',
            height: '500px',
            background: 'white',
            borderRadius: '16px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}>
            {/* Chat Header */}
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '16px 20px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>
                  Insurance Assistant
                </h3>
                <p style={{ margin: '4px 0 0 0', fontSize: '12px', opacity: 0.9 }}>
                  Ask me anything about claims
                </p>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: 'none',
                  color: 'white',
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  fontSize: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ✕
              </button>
            </div>

            {/* Chat Messages */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '20px',
              background: '#F9FAFB'
            }}>
              {chatMessages.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  color: '#9CA3AF'
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
                  <p style={{ fontSize: '14px', margin: 0 }}>
                    Hi! I'm your insurance assistant.
                  </p>
                  <p style={{ fontSize: '13px', marginTop: '8px', color: '#D1D5DB' }}>
                    Ask me about claim procedures, coverage, or policies.
                  </p>
                </div>
              ) : (
                chatMessages.map((msg, index) => (
                  <div
                    key={index}
                    style={{
                      marginBottom: '16px',
                      display: 'flex',
                      justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start'
                    }}
                  >
                    <div style={{
                      maxWidth: '75%',
                      padding: '10px 14px',
                      borderRadius: msg.type === 'user' ? '12px 12px 0 12px' : '12px 12px 12px 0',
                      background: msg.type === 'user' 
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : 'white',
                      color: msg.type === 'user' ? 'white' : '#374151',
                      fontSize: '14px',
                      lineHeight: '1.5',
                      boxShadow: msg.type === 'bot' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none'
                    }}>
                      {msg.text}
                    </div>
                  </div>
                ))
              )}
              
              {chatLoading && (
                <div style={{
                  display: 'flex',
                  justifyContent: 'flex-start',
                  marginBottom: '16px'
                }}>
                  <div style={{
                    background: 'white',
                    padding: '10px 14px',
                    borderRadius: '12px 12px 12px 0',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                  }}>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#D1D5DB',
                        animation: 'bounce 1.4s infinite ease-in-out both'
                      }} />
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#D1D5DB',
                        animation: 'bounce 1.4s infinite ease-in-out both 0.2s'
                      }} />
                      <div style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: '#D1D5DB',
                        animation: 'bounce 1.4s infinite ease-in-out both 0.4s'
                      }} />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form
              onSubmit={handleChatSubmit}
              style={{
                padding: '16px',
                borderTop: '1px solid #E5E7EB',
                background: 'white'
              }}
            >
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type your question..."
                  disabled={chatLoading}
                  style={{
                    flex: 1,
                    padding: '10px 14px',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
                <button
                  type="submit"
                  disabled={chatLoading || !chatInput.trim()}
                  style={{
                    background: chatLoading || !chatInput.trim() 
                      ? '#D1D5DB' 
                      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '10px 16px',
                    fontSize: '18px',
                    cursor: chatLoading || !chatInput.trim() ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  ➤
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes bounce {
          0%, 80%, 100% { 
            transform: scale(0);
          } 
          40% { 
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
};

const StatCard = ({ title, value, icon: Icon, color, bgColor }) => (
  <div style={{
    background: '#FFFFFF',
    borderRadius: '12px',
    padding: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
    border: '1px solid #E5E7EB'
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div>
        <p style={{ color: '#6B7280', fontSize: '13px', fontWeight: '500', marginBottom: '8px' }}>
          {title}
        </p>
        <h3 style={{ color: '#111827', fontSize: '28px', fontWeight: '700', margin: 0 }}>
          {value}
        </h3>
      </div>
      <div style={{
        background: bgColor,
        borderRadius: '10px',
        padding: '10px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Icon size={24} color={color} />
      </div>
    </div>
  </div>
);

export default UserDashboard;
