import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FiLogOut, FiPackage } from 'react-icons/fi';

const Navbar = ({ transparent = false }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav style={{
      background: transparent ? 'transparent' : 'white',
      padding: '20px 0',
      position: transparent ? 'absolute' : 'relative',
      width: '100%',
      zIndex: 100,
      boxShadow: transparent ? 'none' : '0 2px 10px rgba(0,0,0,0.05)'
    }}>
      <div className="container" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}>
          <FiPackage size={32} color={transparent ? 'white' : '#5DCCF5'} />
          <span style={{
            marginLeft: '10px',
            fontSize: '20px',
            fontWeight: '700',
            color: transparent ? 'white' : '#1E3A8A'
          }}>ClaimVerify</span>
        </Link>

        <div style={{ display: 'flex', gap: '30px', alignItems: 'center' }}>
          {user ? (
            <>
              <span style={{ color: transparent ? 'white' : '#6B7280' }}>
                {user.email} ({user.role})
              </span>
              <button
                onClick={handleLogout}
                style={{
                  background: '#EF4444',
                  color: 'white',
                  padding: '10px 24px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
              >
                <FiLogOut /> Logout
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                style={{
                  color: transparent ? 'white' : '#1E3A8A',
                  textDecoration: 'none',
                  fontWeight: '500'
                }}
              >
                Login
              </Link>
              <Link
                to="/register"
                style={{
                  background: 'white',
                  color: '#5DCCF5',
                  padding: '10px 24px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontWeight: '600'
                }}
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
