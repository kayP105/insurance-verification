import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import axios from 'axios';
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  FiFileText, FiAlertTriangle, FiCheckCircle, FiClock, 
  FiTrendingUp, FiTrendingDown, FiDollarSign, FiActivity 
} from 'react-icons/fi';

const AgentDashboard = () => {
  const [claims, setClaims] = useState([]);
  const [stats, setStats] = useState({ 
    total: 0, pending: 0, approved: 0, rejected: 0,
    highRisk: 0, avgFraudScore: 0 
  });
  const [fraudData, setFraudData] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAllClaims();
  }, []);

  const fetchAllClaims = async () => {
    try {
      const response = await axios.get('http://localhost:8000/claims');
      const claimsData = response.data.claims || [];
      setClaims(claimsData);

      const approved = claimsData.filter(c => c.agent_decision === 'approved').length;
      const rejected = claimsData.filter(c => c.agent_decision === 'rejected').length;
      const pending = claimsData.filter(c => 
        c.agent_decision !== 'approved' && c.agent_decision !== 'rejected'
      ).length;

      setStats({
        total: claimsData.length,
        pending: pending,
        approved: approved,
        rejected: rejected,
        highRisk: claimsData.filter(c => 
          (c.tamper_score || 0) >= 0.6 || (c.duplicates && c.duplicates.length > 0)
        ).length, 
        avgFraudScore: claimsData.length > 0
          ? (claimsData.reduce((sum, c) => sum + (c.tamper_score || 0), 0) / claimsData.length) * 100
          : 0
      });


      const fraudScoreRanges = [
        { name: 'Low (0-30%)', value: 0, color: '#10B981' },
        { name: 'Medium (30-60%)', value: 0, color: '#F59E0B' },
        { name: 'High (60-100%)', value: 0, color: '#EF4444' },
      ];

      claimsData.forEach(claim => {
        const score = (claim.tamper_score || 0) * 100;
        if (score < 30) fraudScoreRanges[0].value++;
        else if (score < 60) fraudScoreRanges[1].value++;
        else fraudScoreRanges[2].value++;
      });
      setFraudData(fraudScoreRanges);

      const last7Days = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return {
          date: date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          }),
          claims: 0,
          approved: 0,
          rejected: 0,
        };
      });

      claimsData.forEach(claim => {
        if (!claim.created_at) return;
        const claimDate = new Date(claim.created_at);
        const daysDiff = Math.floor(
          (new Date() - claimDate) / (1000 * 60 * 60 * 24)
        );
        if (daysDiff < 7 && daysDiff >= 0) {
          const index = 6 - daysDiff;
          if (last7Days[index]) {
            const status = claim.agent_decision || claim.status;
            last7Days[index].claims++;
            if (status === 'approved') last7Days[index].approved++;
            if (status === 'rejected') last7Days[index].rejected++;
          }
        }
      });
      setTimelineData(last7Days);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch claims:', error);
      setClaims([]);
      setStats({
        total: 0,
        pending: 0,
        approved: 0,
        rejected: 0,
        highRisk: 0,
        avgFraudScore: 0,
      });
      setFraudData([]);
      setTimelineData([]);
      setLoading(false);
    }
  }; // ← CLOSE fetchAllClaims HERE

  // exportReport OUTSIDE fetchAllClaims
  const exportReport = () => {
    if (claims.length === 0) {
      alert('No claims to export');
      return;
    }

    const headers = ['Claim ID', 'User', 'Type', 'Date', 'Fraud Score', 'Status'];
    const rows = claims.map(claim => [
      `#${String(claim.id).padStart(4, '0')}`,
      claim.filename || 'Unknown',
      'Document',
      new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      `${((claim.tamper_score || 0) * 100).toFixed(1)}%`,
      claim.agent_decision || claim.status || 'Processed'
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `claims_report_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const updateClaimStatus = async (claimId, newStatus) => {
    try {
      await axios.post(`http://localhost:8000/claims/${claimId}/decision`, {
        decision: newStatus,
        note: `Status updated to ${newStatus}`
      });
      alert(`Claim ${newStatus} successfully!`);
      fetchAllClaims();
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update status');
    }
  };

  const StatCard = ({ title, value, icon: Icon, trend, trendValue, color, bgColor }) => (
    <div style={{
      background: '#FFFFFF',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      border: '1px solid #E5E7EB',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ position: 'absolute', top: '-20px', right: '-20px', opacity: 0.1 }}>
        <Icon size={120} color={color} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', position: 'relative', zIndex: 1 }}>
        <div>
          <p style={{ color: '#6B7280', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            {title}
          </p>
          <h2 style={{ color: '#111827', fontSize: '32px', fontWeight: '700', margin: 0 }}>
            {value}
          </h2>
          {trend && (
            <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px', gap: '4px' }}>
              {trend === 'up' ? 
                <FiTrendingUp size={16} color="#10B981" /> : 
                <FiTrendingDown size={16} color="#EF4444" />
              }
              <span style={{ 
                color: trend === 'up' ? '#10B981' : '#EF4444',
                fontSize: '14px',
                fontWeight: '600'
              }}>
                {trendValue}
              </span>
              <span style={{ color: '#9CA3AF', fontSize: '13px' }}>vs last week</span>
            </div>
          )}
        </div>
        <div style={{
          background: bgColor,
          borderRadius: '12px',
          padding: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Icon size={24} color={color} />
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ background: '#F9FAFB', minHeight: '100vh' }}>
      <Navbar />
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px 24px' }}>
        
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>
            Claims Overview
          </h1>
          <p style={{ color: '#6B7280', fontSize: '14px' }}>
            Monitor and manage insurance claims in real-time
          </p>
        </div>

        {/* KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '32px' }}>
          <StatCard 
            title="Total Claims"
            value={stats.total}
            icon={FiFileText}
            trend="up"
            trendValue="+12.5%"
            color="#3B82F6"
            bgColor="#EFF6FF"
          />
          <StatCard 
            title="Pending Review"
            value={stats.pending}
            icon={FiClock}
            color="#F59E0B"
            bgColor="#FEF3C7"
          />
          <StatCard 
            title="Approved"
            value={stats.approved}
            icon={FiCheckCircle}
            trend="up"
            trendValue="+8.2%"
            color="#10B981"
            bgColor="#D1FAE5"
          />
          <StatCard 
            title="High Risk"
            value={stats.highRisk}
            icon={FiAlertTriangle}
            trend="down"
            trendValue="-3.1%"
            color="#EF4444"
            bgColor="#FEE2E2"
          />
        </div>

        {/* Charts Section */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '32px' }}>
          
          {/* Claims Timeline */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            border: '1px solid #E5E7EB'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                Claims Activity
              </h3>
              <p style={{ fontSize: '13px', color: '#6B7280' }}>Last 7 days trend</p>
            </div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip 
                  contentStyle={{ 
                    background: '#FFFFFF',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="claims" stroke="#3B82F6" strokeWidth={3} name="Total Claims" />
                <Line type="monotone" dataKey="approved" stroke="#10B981" strokeWidth={2} name="Approved" />
                <Line type="monotone" dataKey="rejected" stroke="#EF4444" strokeWidth={2} name="Rejected" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Fraud Risk Distribution */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
            border: '1px solid #E5E7EB'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                Risk Distribution
              </h3>
              <p style={{ fontSize: '13px', color: '#6B7280' }}>Fraud score breakdown</p>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={fraudData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {fraudData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ marginTop: '16px' }}>
              {fraudData.map((item, index) => (
                <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: item.color }} />
                    <span style={{ fontSize: '13px', color: '#6B7280' }}>{item.name}</span>
                  </div>
                  <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Claims Table */}
        <div style={{
          background: '#FFFFFF',
          borderRadius: '16px',
          padding: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          border: '1px solid #E5E7EB'
        }}>
          <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '4px' }}>
                Recent Claims
              </h3>
              <p style={{ fontSize: '13px', color: '#6B7280' }}>Manage and review claim submissions</p>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                onClick={() => navigate('/fraud-graph')}
                style={{
                  background: '#8B5CF6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <FiActivity size={18} />
                Fraud Network
              </button>
              <button 
                onClick={exportReport}
                style={{
                  background: '#3B82F6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                Export Report
              </button>

            </div>
          </div>

          {claims.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: '#9CA3AF' }}>
              <FiFileText size={48} style={{ margin: '0 auto 16px' }} />
              <p>No claims available</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: '0 8px' }}>
                <thead>
                  <tr style={{ background: '#F9FAFB' }}>
                    <th style={tableHeaderStyle}>CLAIM ID</th>
                    <th style={tableHeaderStyle}>USER</th>
                    <th style={tableHeaderStyle}>TYPE</th>
                    <th style={tableHeaderStyle}>DATE</th>
                    <th style={tableHeaderStyle}>FRAUD SCORE</th>
                    <th style={tableHeaderStyle}>DUPLICATE</th>  {/* ADD THIS */}
                    <th style={tableHeaderStyle}>STATUS</th>
                    <th style={tableHeaderStyle}>ACTIONS</th>
                  </tr>
                </thead>

                <tbody>
                  {claims.map((claim, index) => {
                    const isDuplicate = claim.duplicates && claim.duplicates.length > 0;
                    const baseFraudScore = (claim.tamper_score || 0) * 100;
                    // Boost visual score if duplicate detected
                    const fraudScore = isDuplicate ? Math.min(baseFraudScore + 20, 100) : baseFraudScore;
                    const fraudColor = fraudScore > 70 ? '#EF4444' : fraudScore > 40 ? '#F59E0B' : '#10B981';
                    
                    return (
                      <tr key={claim.id} style={{
                        background: index % 2 === 0 ? '#F9FAFB' : '#FFFFFF',
                        transition: 'all 0.2s'
                      }}>
                        <td style={tableCellStyle}>
                          <span style={{ fontFamily: 'monospace', color: '#3B82F6', fontWeight: '600' }}>
                            #{String(claim.id).padStart(4, '0')}
                          </span>
                        </td>
                        <td style={tableCellStyle}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '50%',
                              background: '#3B82F6',
                              color: 'white',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '12px',
                              fontWeight: '600'
                            }}>
                              {(claim.filename || 'U').charAt(0).toUpperCase()}
                            </div>
                            <span style={{ fontSize: '14px' }}>{claim.filename || 'Unknown'}</span>
                          </div>
                        </td>
                        <td style={tableCellStyle}>
                          <span style={{
                            background: '#EFF6FF',
                            color: '#3B82F6',
                            padding: '4px 12px',
                            borderRadius: '12px',
                            fontSize: '13px',
                            fontWeight: '500',
                            textTransform: 'capitalize'
                          }}>
                            Document
                          </span>
                        </td>
                        <td style={tableCellStyle}>
                          {new Date().toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric',
                            year: 'numeric'
                          })}
                        </td>
                        <td style={tableCellStyle}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{
                              width: '60px',
                              height: '6px',
                              background: '#E5E7EB',
                              borderRadius: '3px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${fraudScore.toFixed(1)}%`,
                                height: '100%',
                                background: fraudColor,
                                borderRadius: '3px'
                              }} />
                            </div>
                            <span style={{ color: fraudColor, fontWeight: '600', fontSize: '14px' }}>
                              {fraudScore.toFixed(1)}%
                            </span>
                          </div>
                        </td>
                        
                        {/* NEW DUPLICATE COLUMN */}
                        <td style={tableCellStyle}>
                          {isDuplicate ? (
                            <span style={{
                              background: '#FEF3C7',
                              color: '#92400E',
                              padding: '6px 12px',
                              borderRadius: '12px',
                              fontSize: '13px',
                              fontWeight: '600',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}>
                              <FiAlertTriangle size={14} />
                              {claim.duplicates.length} Match{claim.duplicates.length > 1 ? 'es' : ''}
                            </span>
                          ) : (
                            <span style={{ color: '#10B981', fontSize: '13px', fontWeight: '600' }}>
                              ✓ Clean
                            </span>
                          )}
                        </td>

                        <td style={tableCellStyle}>
                          <span style={{
                            background: claim.agent_decision === 'approved' ? '#D1FAE5' : 
                                      claim.agent_decision === 'rejected' ? '#FEE2E2' : '#FEF3C7',
                            color: claim.agent_decision === 'approved' ? '#065F46' : 
                                  claim.agent_decision === 'rejected' ? '#991B1B' : '#92400E',
                            padding: '6px 12px',
                            borderRadius: '12px',
                            fontSize: '13px',
                            fontWeight: '600',
                            textTransform: 'capitalize'
                          }}>
                            {claim.agent_decision || claim.status || 'Processed'}
                          </span>
                        </td>
                        <td style={tableCellStyle}>
                          <button 
                            onClick={() => navigate(`/claim/${claim.id}`)}
                            style={{
                              background: '#3B82F6',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '8px 16px',
                              fontSize: '13px',
                              fontWeight: '500',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px'
                            }}
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>

              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


const tableHeaderStyle = {
  textAlign: 'left',
  padding: '12px 16px',
  color: '#6B7280',
  fontWeight: '600',
  fontSize: '13px',
  textTransform: 'uppercase',
  letterSpacing: '0.5px'
};


const tableCellStyle = {
  padding: '16px',
  color: '#374151',
  fontSize: '14px'
};


export default AgentDashboard