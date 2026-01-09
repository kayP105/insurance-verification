import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import axios from 'axios';

const ContactAgent = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');

  const sendMessage = async () => {
    if (!message.trim()) return;

    try {
      await axios.post('http://localhost:8000/contact_agent', {
        claim_id: id,
        message: message
      });
      alert('Message sent to agent successfully!');
      navigate(-1);
    } catch (err) {
      alert('Failed to send message');
    }
  };

  return (
    <div style={{ background: '#F0F9FF', minHeight: '100vh' }}>
      <Navbar />
      <div className="container" style={{ paddingTop: '40px' }}>
        <h2>Contact Agent</h2>
        <p>Explain why you think your claim was wrongly flagged.</p>

        <textarea
          rows="5"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{
            width: '100%',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid #E5E7EB',
            marginBottom: '15px'
          }}
        />

        <button
          onClick={sendMessage}
          style={{
            background: '#3B82F6',
            color: 'white',
            padding: '10px 20px',
            borderRadius: '8px',
            border: 'none',
            fontWeight: '600'
          }}
        >
          Send to Agent
        </button>
      </div>
    </div>
  );
};

export default ContactAgent;
