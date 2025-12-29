import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { FiPlay, FiShield, FiZap, FiTrendingUp, FiCheckCircle, FiArrowRight } from 'react-icons/fi';

const Landing = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const features = [
    {
      icon: <FiShield size={36} />,
      title: 'AI-Powered Fraud Detection',
      description: 'Advanced machine learning algorithms detect document tampering and fraudulent claims with 95% accuracy'
    },
    {
      icon: <FiZap size={36} />,
      title: 'Instant Verification',
      description: 'Process claims in seconds with automated OCR and intelligent document analysis'
    },
    {
      icon: <FiTrendingUp size={36} />,
      title: 'Real-Time Analytics',
      description: 'Comprehensive dashboard with fraud score visualization and claim status tracking'
    }
  ];

  const stats = [
    { value: '95%', label: 'Fraud Detection Accuracy' },
    { value: '10x', label: 'Faster Processing' },
    { value: '24/7', label: 'Automated Monitoring' }
  ];

  return (
    <div style={{ background: '#F0F7FF', overflow: 'hidden' }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #E0F2FE 0%, #BAE6FD 100%)',
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Subtle Background Elements */}
        <div style={{
          position: 'absolute',
          top: '5%',
          right: '10%',
          width: '500px',
          height: '500px',
          background: 'radial-gradient(circle, rgba(125,211,252,0.15) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 8s ease-in-out infinite'
        }} />
        <div style={{
          position: 'absolute',
          bottom: '10%',
          left: '5%',
          width: '350px',
          height: '350px',
          background: 'radial-gradient(circle, rgba(147,197,253,0.12) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 10s ease-in-out infinite reverse'
        }} />

        <Navbar transparent={true} />
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: '55% 45%',
          minHeight: 'calc(100vh - 80px)',
          alignItems: 'center'
        }}>
          {/* Left Content */}
          <div style={{
            paddingLeft: 'max(5%, 60px)',
            paddingRight: '40px',
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateX(0)' : 'translateX(-50px)',
            transition: 'all 0.8s ease-out'
          }}>
            <div style={{
              display: 'inline-block',
              background: 'white',
              padding: '10px 24px',
              borderRadius: '25px',
              marginBottom: '32px',
              border: '1px solid rgba(125, 211, 252, 0.3)',
              boxShadow: '0 4px 15px rgba(14, 165, 233, 0.12)'
            }}>
              <span style={{
                background: 'linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontSize: '13px',
                fontWeight: '700',
                letterSpacing: '1px'
              }}>
                ✨ AI-POWERED INSURANCE VERIFICATION
              </span>
            </div>

            <h1 style={{
              fontSize: '68px',
              color: '#0C4A6E',
              fontWeight: '800',
              marginBottom: '28px',
              lineHeight: '1.1',
              letterSpacing: '-2.5px'
            }}>
              WE ARE BUILDING
              <br />
              <span style={{
                position: 'relative',
                display: 'inline-block'
              }}>
                <span style={{
                  position: 'relative',
                  zIndex: 2,
                  color: '#0C4A6E'
                }}>
                  SOFTWARE
                </span>
                <span style={{
                  position: 'absolute',
                  bottom: '8px',
                  left: '0',
                  right: '0',
                  height: '20px',
                  background: 'linear-gradient(135deg, #7DD3FC 0%, #BAE6FD 100%)',
                  zIndex: 1,
                  borderRadius: '4px'
                }} />
              </span>
              {' '}TO HELP
            </h1>

            <p style={{
              color: '#0369A1',
              fontSize: '19px',
              lineHeight: '1.7',
              marginBottom: '44px',
              maxWidth: '560px',
              fontWeight: '400'
            }}>
              Automate insurance claim verification with cutting-edge AI. 
              Detect fraud, analyze documents, and track claims in real-time with explainable AI technology.
            </p>

            <div style={{ display: 'flex', gap: '16px', alignItems: 'center', marginBottom: '60px' }}>
              {/* MAIN CHANGE: navigate('/register') */}
              <button
                onClick={() => navigate('/register')}
                style={{
                  background: 'linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%)',
                  color: 'white',
                  padding: '16px 36px',
                  borderRadius: '12px',
                  fontWeight: '600',
                  fontSize: '16px',
                  boxShadow: '0 8px 25px rgba(14, 165, 233, 0.35)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = 'translateY(-2px)';
                  e.target.style.boxShadow = '0 12px 35px rgba(14, 165, 233, 0.45)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = '0 8px 25px rgba(14, 165, 233, 0.35)';
                }}
              >
                Get Started <FiArrowRight />
              </button>

              {/* <button
                style={{
                  background: 'white',
                  color: '#0369A1',
                  padding: '16px 28px',
                  borderRadius: '12px',
                  fontWeight: '600',
                  fontSize: '16px',
                  border: '1px solid rgba(125, 211, 252, 0.4)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  transition: 'all 0.3s ease',
                  boxShadow: '0 4px 15px rgba(125, 211, 252, 0.15)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = '#F0F9FF';
                  e.target.style.transform = 'translateY(-2px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'white';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                <FiPlay /> Watch Demo
              </button> */}
            </div>

            {/* Stats Row */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '32px'
            }}>
              {stats.map((stat, idx) => (
                <div key={idx}>
                  <div style={{
                    fontSize: '36px',
                    fontWeight: '800',
                    background: 'linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    marginBottom: '6px',
                    letterSpacing: '-1px'
                  }}>
                    {stat.value}
                  </div>
                  <div style={{
                    fontSize: '13px',
                    color: '#0369A1',
                    fontWeight: '600',
                    letterSpacing: '0.3px'
                  }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Content - Full Height Dashboard */}
          <div style={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '40px 60px 40px 0',
            opacity: isVisible ? 1 : 0,
            transform: isVisible ? 'translateX(0)' : 'translateX(50px)',
            transition: 'all 0.8s ease-out 0.2s'
          }}>
            {/* Glassmorphic Card */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.7)',
              backdropFilter: 'blur(20px)',
              borderRadius: '28px',
              padding: '24px',
              border: '1px solid rgba(255, 255, 255, 0.9)',
              boxShadow: '0 25px 70px rgba(14, 165, 233, 0.18)',
              position: 'relative',
              width: '100%',
              maxWidth: '650px'
            }}>
              {/* Dashboard Image */}
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=900&h=600&fit=crop"
                alt="Dashboard Preview"
                style={{
                  width: '100%',
                  borderRadius: '20px',
                  boxShadow: '0 15px 40px rgba(14, 165, 233, 0.25)',
                  display: 'block'
                }}
              />

              {/* Floating Badge - Top Right */}
              <div style={{
                position: 'absolute',
                top: '50px',
                right: '50px',
                background: 'linear-gradient(135deg, #86EFAC 0%, #4ADE80 100%)',
                padding: '14px 22px',
                borderRadius: '14px',
                color: '#064E3B',
                fontWeight: '700',
                fontSize: '15px',
                boxShadow: '0 12px 28px rgba(74, 222, 128, 0.4)',
                animation: 'float 3s ease-in-out infinite',
                border: '2px solid rgba(255, 255, 255, 0.6)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiCheckCircle size={18} />
                <span>95% Accuracy</span>
              </div>

              {/* Floating Badge - Bottom Left */}
              <div style={{
                position: 'absolute',
                bottom: '50px',
                left: '50px',
                background: 'linear-gradient(135deg, #BAE6FD 0%, #7DD3FC 100%)',
                padding: '14px 22px',
                borderRadius: '14px',
                color: '#0C4A6E',
                fontWeight: '700',
                fontSize: '15px',
                boxShadow: '0 12px 28px rgba(125, 211, 252, 0.4)',
                animation: 'float 3s ease-in-out infinite 1.5s',
                border: '2px solid rgba(255, 255, 255, 0.6)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <FiZap size={18} />
                <span>Real-Time Analysis</span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div style={{
          position: 'absolute',
          bottom: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          animation: 'bounce 2s infinite'
        }}>
          <div style={{
            width: '28px',
            height: '48px',
            border: '2px solid rgba(14, 165, 233, 0.35)',
            borderRadius: '20px',
            position: 'relative'
          }}>
            <div style={{
              width: '5px',
              height: '9px',
              background: 'rgba(14, 165, 233, 0.6)',
              borderRadius: '3px',
              position: 'absolute',
              top: '8px',
              left: '50%',
              transform: 'translateX(-50%)',
              animation: 'scroll 2s infinite'
            }} />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div style={{ padding: '120px 0', background: '#F0F7FF' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <div style={{
              display: 'inline-block',
              background: 'linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontSize: '15px',
              fontWeight: '700',
              letterSpacing: '1.5px',
              marginBottom: '18px'
            }}>
              POWERFUL FEATURES
            </div>
            <h2 style={{
              fontSize: '52px',
              fontWeight: '800',
              color: '#0C4A6E',
              marginBottom: '24px',
              letterSpacing: '-1.5px'
            }}>
              How It Works
            </h2>
            <p style={{
              color: '#0369A1',
              fontSize: '19px',
              maxWidth: '720px',
              margin: '0 auto',
              lineHeight: '1.7'
            }}>
              Our AI-powered system combines computer vision, natural language processing, 
              and machine learning to deliver unparalleled accuracy in claim verification.
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '32px'
          }}>
            {features.map((feature, index) => (
              <div
                key={index}
                style={{
                  background: 'white',
                  padding: '44px',
                  borderRadius: '20px',
                  boxShadow: '0 4px 20px rgba(14, 165, 233, 0.08)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                  border: '1px solid rgba(186, 230, 253, 0.4)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-10px)';
                  e.currentTarget.style.boxShadow = '0 25px 50px rgba(14, 165, 233, 0.15)';
                  e.currentTarget.style.borderColor = '#7DD3FC';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(14, 165, 233, 0.08)';
                  e.currentTarget.style.borderColor = 'rgba(186, 230, 253, 0.4)';
                }}
              >
                <div style={{
                  width: '72px',
                  height: '72px',
                  background: 'linear-gradient(135deg, #BAE6FD 0%, #7DD3FC 100%)',
                  borderRadius: '18px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#0369A1',
                  marginBottom: '28px',
                  boxShadow: '0 10px 30px rgba(125, 211, 252, 0.3)'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{
                  fontSize: '22px',
                  fontWeight: '700',
                  color: '#0C4A6E',
                  marginBottom: '14px',
                  letterSpacing: '-0.3px'
                }}>
                  {feature.title}
                </h3>
                <p style={{
                  color: '#0369A1',
                  lineHeight: '1.7',
                  fontSize: '16px'
                }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div style={{
        background: 'linear-gradient(135deg, #BAE6FD 0%, #7DD3FC 100%)',
        padding: '100px 0',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: '-120px',
          right: '-120px',
          width: '450px',
          height: '450px',
          background: 'radial-gradient(circle, rgba(224,242,254,0.4) 0%, transparent 70%)',
          borderRadius: '50%'
        }} />

        <div className="container" style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
          <h2 style={{
            fontSize: '52px',
            fontWeight: '800',
            color: '#0C4A6E',
            marginBottom: '28px',
            letterSpacing: '-1.5px'
          }}>
            Ready to Transform Your Claims Process?
          </h2>
          <p style={{
            color: '#0369A1',
            fontSize: '19px',
            marginBottom: '44px',
            maxWidth: '650px',
            margin: '0 auto 44px',
            lineHeight: '1.7'
          }}>
            Join leading insurance providers using AI to detect fraud and streamline verification
          </p>
          {/* SECOND CHANGE: CTA also goes to /register */}
          <button
            onClick={() => navigate('/register')}
            style={{
              background: 'white',
              color: '#0369A1',
              padding: '20px 56px',
              borderRadius: '14px',
              fontWeight: '700',
              fontSize: '18px',
              boxShadow: '0 12px 35px rgba(255, 255, 255, 0.5)',
              transition: 'all 0.3s ease',
              border: 'none'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-4px)';
              e.target.style.boxShadow = '0 18px 45px rgba(255, 255, 255, 0.6)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 12px 35px rgba(255, 255, 255, 0.5)';
            }}
          >
            Start Free Trial
          </button>
        </div>
      </div>

      {/* Add CSS Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
        }
        
        @keyframes bounce {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(-10px); }
        }
        
        @keyframes scroll {
          0% { top: 8px; opacity: 1; }
          100% { top: 26px; opacity: 0; }
        }
      `}</style>
    </div>
  );
};

export default Landing;
