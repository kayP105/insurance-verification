import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [docId, setDocId] = useState(null);
  const [status, setStatus] = useState(null);
  const [extractedData, setExtractedData] = useState(null);

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
    setDocId(null);
    setStatus(null);
    setExtractedData(null);
  };

  const onUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(res.data.message);
      setDocId(res.data.doc_id);
    } catch (err) {
      setMessage('Upload failed.');
      console.error(err);
    }
  };

  const onCheckStatus = async () => {
    if (!docId) return;
    try {
      const res = await axios.get(`http://localhost:8000/status/${docId}`);
      setStatus(res.data.status);
      if (res.data.data) {
        setExtractedData(res.data.data);
      }
    } catch (err) {
      setStatus('Failed to get status.');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>AI Insurance Verification 🧾</h2>
        <input type="file" onChange={onFileChange} />
        <button onClick={onUpload} disabled={!file}>
          Upload Document
        </button>
        {message && <p>{message}</p>}

        {docId && (
          <div className="status-checker">
            <hr />
            <p>Document ID: {docId}</p>
            <button onClick={onCheckStatus}>Check Status</button>
            {status && <p><strong>Status: {status}</strong></p>}
            {extractedData && (
              <pre className="data-preview">
                {JSON.stringify(extractedData, null, 2)}
              </pre>
            )}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;