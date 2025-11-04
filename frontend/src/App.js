import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const BASE_URL = 'http://localhost:8000';

function App() {
  // --- Input States ---
  const [file, setFile] = useState(null);
  const [claimAmount, setClaimAmount] = useState(50000); // Default claim amount set to a common value
  
  // --- Process/Feedback States ---
  const [message, setMessage] = useState('');
  const [docId, setDocId] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // --- OCR/Status States ---
  const [ocrStatus, setOcrStatus] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  
  // --- Workflow Results States ---
  const [workflowResult, setWorkflowResult] = useState(null);
  const [workflowError, setWorkflowError] = useState(null);

  const resetState = () => {
    setMessage('');
    setDocId(null);
    setOcrStatus(null);
    setExtractedData(null);
    setWorkflowResult(null);
    setWorkflowError(null);
  };

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    resetState();
  };

  // --- Step 1: Upload and Start OCR ---
  const onUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setMessage('Uploading document and initiating Smart OCR...');
    setIsProcessing(true);

    try {
      const res = await axios.post(`${BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage(res.data.message);
      setDocId(res.data.doc_id);
    } catch (err) {
      setMessage('Upload failed. Check the server terminal for details.');
      console.error('Upload Error:', err);
    } finally {
        setIsProcessing(false);
    }
  };

  // --- Step 2: Check OCR Status ---
  const onCheckStatus = async () => {
    if (!docId) return;
    setMessage(`Fetching status for Document ID: ${docId}`);
    try {
      const res = await axios.get(`${BASE_URL}/status/${docId}`);
      setOcrStatus(res.data.status);
      setExtractedData(res.data.data);
      if (res.data.status === 'processed') {
          setMessage(`OCR Complete. Ready for Workflow.`);
      } else if (res.data.status === 'failed_ocr' || res.data.status === 'failed') {
          setMessage(`OCR Failed. Check Extracted Data for error details.`);
      }
    } catch (err) {
      setOcrStatus('Failed to get status.');
      setMessage('Failed to connect to status endpoint.');
      console.error('Status Check Error:', err);
    }
  };
  
  // --- Step 3: Run Full Workflow ---
  const onProcessWorkflow = async () => {
    if (!docId || ocrStatus !== 'processed') {
      alert('OCR must be "processed" before running the workflow.');
      return;
    }
    
    setIsProcessing(true);
    setWorkflowResult(null);
    setWorkflowError(null);
    setMessage('Executing verification, ML models, and rule engine...');

    try {
      const res = await axios.post(`${BASE_URL}/process_full_claim`, {
        doc_id: docId,
        claim_amount: parseFloat(claimAmount),
      });
      
      const result = res.data;
      
      if (result && result.decision) {
          setWorkflowResult(result);
          setMessage(`Workflow complete: ${result.decision}`);
      } else {
          // Fallback for unexpected successful response structure
          setWorkflowError(result.error || 'Workflow completed, but missing final decision.');
          setMessage('Workflow completed with an error!');
      }
      
      // Update the status display one last time
      const statusRes = await axios.get(`${BASE_URL}/status/${docId}`);
      setOcrStatus(statusRes.data.status);

    } catch (err) {
      // Handle HTTP errors
      const errorData = err.response?.data || err;
      setWorkflowError(errorData.error || 'A critical server error occurred during workflow execution.');
      setMessage('Workflow failed!');
      console.error('Workflow Error:', errorData);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2 className="app-title">
            <span role="img" aria-label="Robot Head">🤖</span> AI Policy Verification Pipeline
        </h2>
        
        {/* Global Feedback */}
        {message && <p className="global-message">{message}</p>}

        <div className="process-grid">
            
            {/* --- CARD 1: UPLOAD & OCR --- */}
            <div className="card step-card">
                <div className="card-header">1. Document Ingestion (S3/Lambda Mock)</div>
                <label className="file-upload-label">
                    Choose PDF Policy Statement
                    <input type="file" onChange={onFileChange} accept=".pdf" style={{display: 'none'}} />
                </label>
                {file && <p className="file-name">{file.name}</p>}
                
                <button onClick={onUpload} disabled={!file || isProcessing}>
                    {isProcessing && docId === null ? 'Uploading...' : 'Upload & Start OCR'}
                </button>
            </div>

            {/* --- CARD 2: STATUS & PREVIEW --- */}
            <div className={`card status-card ${docId ? 'active' : 'inactive'}`}>
                <div className="card-header">2. OCR Extraction Status (RDS Mock)</div>
                <p className="status-line">Document ID: <strong>{docId || 'N/A'}</strong></p>
                
                <button onClick={onCheckStatus} disabled={!docId || isProcessing}>
                    Check Status
                </button>
                
                {ocrStatus && (
                    <p className={`status-badge status-${ocrStatus.split(':')[0]}`}>
                        Status: <strong>{ocrStatus}</strong>
                    </p>
                )}

                {extractedData && Object.keys(extractedData).length > 0 && (
                    <div className="data-preview-container">
                        <p className="preview-title">OCR Data Snapshot:</p>
                        <pre className="data-preview">
                            {JSON.stringify({
                                policy_no: extractedData.policy_no,
                                name: extractedData.name,
                                limit: extractedData.liability_limit,
                                type: extractedData.policy_type
                            }, null, 2)}
                        </pre>
                    </div>
                )}
            </div>

            {/* --- CARD 3: WORKFLOW EXECUTION --- */}
            <div className={`card workflow-card ${ocrStatus === 'processed' ? 'active' : 'inactive'}`}>
                <div className="card-header">3. Workflow Execution (Step Function Mock)</div>
                
                <label htmlFor="claim-amount-input" className="input-label">Claim Amount (Manual Input):</label>
                <input 
                    id="claim-amount-input"
                    type="number" 
                    value={claimAmount} 
                    onChange={(e) => setClaimAmount(e.target.value)} 
                    min="1000"
                    className="claim-input"
                    disabled={ocrStatus !== 'processed' || isProcessing}
                />
                
                <button 
                    onClick={onProcessWorkflow} 
                    disabled={ocrStatus !== 'processed' || isProcessing || !claimAmount}
                    className="workflow-button"
                >
                    {isProcessing ? 'Executing Rules & Models...' : 'Run Full Workflow'}
                </button>
            </div>
            
        </div>
        
        {/* --- FINAL DECISION PANEL --- */}
        <div className="final-panel">
            <h3>Final Workflow Decision</h3>
            {workflowResult && (
                <>
                    <div className={`final-decision decision-${workflowResult.decision}`}>
                        {workflowResult.decision.replace('_', ' ')}
                    </div>
                    <p className="reason-text">Reason: **{workflowResult.reason}**</p>
                    
                    <details className="full-data-details">
                        <summary>Click to view Full Workflow Trace (JSON)</summary>
                        <pre className="data-preview full-trace-preview">
                            {JSON.stringify(workflowResult.all_data, null, 2)}
                        </pre>
                    </details>
                </>
            )}

            {workflowError && <p className="error-text">Workflow Error: {workflowError}</p>}
            
            {!workflowResult && !workflowError && ocrStatus === 'processed' && 
                <p className="prompt-text">Input a claim amount and click "Run Full Workflow" to execute the rule engine.</p>
            }
        </div>
      </header>
    </div>
  );
}

export default App;