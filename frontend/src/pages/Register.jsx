import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { FiMail, FiLock, FiUser } from 'react-icons/fi';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
  e.preventDefault();
  setError('');
  setLoading(true);

  try {
    console.log('Sending:', { username: email, password: password });
    await axios.post('http://localhost:8000/signup', {
      username: name || email,
      email: email,
      password: password,
      role: role,  // Send the selected role!
    });

    
    alert('Account created successfully!');
    navigate('/login');
  } catch (err) {
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(e => e.msg).join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Signup failed');
      }
    } else {
      setError('Signup failed');
    }
  } finally {
    setLoading(false);
  }
};



  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 50%, #7DD3FC 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '24px',
        padding: '40px',
        width: '100%',
        maxWidth: '480px',
        boxShadow: '0 20px 60px rgba(15,23,42,0.15)'
      }}>
        <h2 style={{
          fontSize: '32px',
          fontWeight: '700',
          color: '#0C4A6E',
          marginBottom: '6px',
          textAlign: 'center'
        }}>
          Create Account
        </h2>
        <p style={{
          color: '#64748B',
          textAlign: 'center',
          marginBottom: '24px'
        }}>
          Sign up to start verifying insurance claims
        </p>

        {error && (
          <div style={{
            background: '#FEE2E2',
            color: '#991B1B',
            padding: '10px 12px',
            borderRadius: '8px',
            marginBottom: '16px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Role selector */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#0C4A6E',
              fontWeight: '500'
            }}>
              Register As
            </label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="button"
                onClick={() => setRole('user')}
                style={{
                  flex: 1,
                  padding: '10px',
                  borderRadius: '10px',
                  border: `2px solid ${role === 'user' ? '#0EA5E9' : '#E5E7EB'}`,
                  background: role === 'user' ? '#E0F2FE' : 'white',
                  color: role === 'user' ? '#0C4A6E' : '#6B7280',
                  fontWeight: '600'
                }}
              >
                <FiUser style={{ marginRight: 6 }} />
                User
              </button>
              <button
                type="button"
                onClick={() => setRole('agent')}
                style={{
                  flex: 1,
                  padding: '10px',
                  borderRadius: '10px',
                  border: `2px solid ${role === 'agent' ? '#0EA5E9' : '#E5E7EB'}`,
                  background: role === 'agent' ? '#E0F2FE' : 'white',
                  color: role === 'agent' ? '#0C4A6E' : '#6B7280',
                  fontWeight: '600'
                }}
              >
                <FiUser style={{ marginRight: 6 }} />
                Agent
              </button>
            </div>
          </div>

          {/* Name */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#0C4A6E',
              fontWeight: '500'
            }}>
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="John Doe"
              style={{
                width: '100%',
                padding: '11px 12px',
                borderRadius: '10px',
                border: '2px solid #E5E7EB',
                fontSize: '15px',
                background: '#F9FAFB'
              }}
            />
          </div>

          {/* Email */}
          <div style={{ marginBottom: '18px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#0C4A6E',
              fontWeight: '500'
            }}>
              <FiMail style={{ marginRight: 6 }} />
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="you@example.com"
              style={{
                width: '100%',
                padding: '11px 12px',
                borderRadius: '10px',
                border: '2px solid #E5E7EB',
                fontSize: '15px',
                background: '#F9FAFB'
              }}
            />
          </div>
          
          {/* Password */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              marginBottom: '8px',
              color: '#0C4A6E',
              fontWeight: '500'
            }}>
              <FiLock style={{ marginRight: 6 }} />
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              placeholder="At least 6 characters"
              style={{
                width: '100%',
                padding: '11px 12px',
                borderRadius: '10px',
                border: '2px solid #E5E7EB',
                fontSize: '15px',
                background: '#F9FAFB'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '13px',
              background: loading ? '#9CA3AF' : 'linear-gradient(135deg,#0EA5E9,#06B6D4)',
              color: 'white',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              border: 'none',
              cursor: loading ? 'default' : 'pointer',
              boxShadow: '0 10px 25px rgba(14,165,233,0.35)'
            }}
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <p style={{
          marginTop: '18px',
          fontSize: '14px',
          color: '#6B7280',
          textAlign: 'center'
        }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#0EA5E9', fontWeight: 600 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
