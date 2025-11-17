import React, { useState } from 'react';
import { askTextToSqlApi, runDiagnosticsApi } from './api/apiClient.js';

// --- Main App Component (Now a Router) ---
// This component now manages which page is visible
function App() {
  // 'home', 'text-to-sql', or 'diagnostics'
  const [page, setPage] = useState('home');

  // Helper function to render the correct page
  const renderPage = () => {
    switch (page) {
      case 'text-to-sql':
        return (
          <PageWrapper setPage={setPage}>
            <TextToSqlInterface />
          </PageWrapper>
        );
      case 'diagnostics':
        return (
          <PageWrapper setPage={setPage}>
            <DiagnosticsInterface />
          </PageWrapper>
        );
      case 'home':
      default:
        return <HomePage setPage={setPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-200 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <Header />
        <main>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

// --- Page Wrapper (for the "Back" button) ---
const PageWrapper = ({ children, setPage }) => (
  <div>
    <button
      onClick={() => setPage('home')}
      className="mb-6 text-sm text-blue-400 hover:text-blue-300 transition duration-300"
    >
      &larr; Back to Home
    </button>
    {children}
  </div>
);

// --- New Home Page Component ---
function HomePage({ setPage }) {
  return (
    <div className="text-center">
      <h2 className="text-2xl font-light text-slate-300 mb-10">
        Welcome. Please select a tool to get started.
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        
        {/* Button for Text-to-SQL */}
        <div
          onClick={() => setPage('text-to-sql')}
          className="group bg-slate-800 p-8 rounded-lg shadow-lg border border-slate-700 hover:border-blue-500 transition-all duration-300 cursor-pointer"
        >
          <h3 className="text-3xl font-bold text-slate-100 mb-3 group-hover:text-blue-400 transition-colors">
            Query Database
          </h3>
          <p className="text-slate-400">
            Use the "Librarian" to ask free-form, natural language questions to the customer database.
          </p>
        </div>

        {/* Button for Diagnostics */}
        <div
          onClick={() => setPage('diagnostics')}
          className="group bg-slate-800 p-8 rounded-lg shadow-lg border border-slate-700 hover:border-indigo-500 transition-all duration-300 cursor-pointer"
        >
          <h3 className="text-3xl font-bold text-slate-100 mb-3 group-hover:text-indigo-400 transition-colors">
            Run Diagnosis
          </h3>
          <p className="text-slate-400">
            Use the "Detective" to run a complex, multi-step investigation on a specific product.
          </p>
        </div>

      </div>
    </div>
  );
}


// --- Helper Components (All in one file) ---

function Header() {
  return (
    <header className="w-full mb-10">
      <h1 className="text-4xl font-bold text-center text-slate-100">
        Customer Diagnostics Platform
      </h1>
    </header>
  );
}

function TextToSqlInterface() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError('Please enter a question.');
      return;
    }
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await askTextToSqlApi(question);
      setResult(response);
    } catch (err) {
      if (err.response) {
        console.error("Server responded with an error:", err.response.data);
        setError(`Error from server: ${err.response.data.detail || err.message}`);
      } else if (err.request) {
        console.error("No response received from server:", err.request);
        setError('The Text-to-SQL service is not responding. Please check its logs.');
      } else {
        console.error('Error setting up request:', err.message);
        setError(err.message || 'An unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
      <h2 className="text-2xl font-bold text-slate-100 mb-4">Query Database with Natural Language</h2>
      <textarea
        className="w-full h-32 p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
        placeholder="e.g., 'Show me all open support tickets for the Quantum Laptop'"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        disabled={isLoading}
      />
      <button
        onClick={handleAskQuestion}
        className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300 disabled:opacity-50"
        disabled={isLoading}
      >
        {isLoading ? 'Asking...' : 'Ask Question'}
      </button>

      <div className="mt-6">
        <h3 className="text-xl font-semibold text-slate-200 mb-2">Results:</h3>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 min-h-[100px] text-slate-300 font-mono text-sm">
          {isLoading && <p>Awaiting query...</p>}
          {error && <p className="text-red-400 whitespace-pre-wrap">{error}</p>}
          {result && (
            <pre className="whitespace-pre-wrap break-all">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
          {!isLoading && !error && !result && <p className="text-slate-500">Results will appear here.</p>}
        </div>
      </div>
    </div>
  );
}

function DiagnosticsInterface() {
  const [productId, setProductId] = useState('');
  const [productName, setProductName] = useState('');
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRunDiagnosis = async () => {
    if (!productId.trim() || !productName.trim()) {
      setError('Please enter both a Product ID and a Product Name.');
      return;
    }
    setIsLoading(true);
    setError('');
    setReport(null);
    try {
      const response = await runDiagnosticsApi(parseInt(productId), productName);
      setReport(response);
    } catch (err) {
      if (err.response) {
        console.error("Server responded with an error:", err.response.data);
        setError(`Error from server: ${err.response.data.detail || err.message}`);
      } else if (err.request) {
        console.error("No response received from server:", err.request);
        setError('The Diagnostics service is not responding. Please check its logs.');
      } else {
        console.error('Error setting up request:', err.message);
        setError(err.message || 'An unknown error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Helper component to render the neat report
  const RenderReport = ({ report }) => (
    <div className="space-y-4">
      {/* 1. Show the Summary First */}
      <div>
        <h4 className="font-semibold text-slate-100 mb-1">Summary</h4>
        <p className="text-slate-300">{report.summary}</p>
      </div>
      
      {/* 2. Show the Raw Data Neatly */}
      <div>
        <h4 className="font-semibold text-slate-100 mb-2">Raw Data Gathered</h4>
        <div className="space-y-3">
          {Object.entries(report.raw_data).map(([question, data]) => (
            <div key={question}>
              <p className="text-slate-400 text-xs font-medium">{question}</p>
              {data.length > 0 ? (
                <pre className="whitespace-pre-wrap break-all text-xs p-2 bg-slate-800 rounded-md mt-1">
                  {JSON.stringify(data, null, 2)}
                </pre>
              ) : (
                <p className="text-slate-500 text-xs italic">No data found.</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
      <h2 className="text-2xl font-bold text-slate-100 mb-4">Run Product Diagnosis</h2>
      <div className="space-y-4">
        <input
          type="text"
          className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          placeholder="Product ID (e.g., 101)"
          value={productId}
          onChange={(e) => setProductId(e.target.value)}
          disabled={isLoading}
        />
        <input
          type="text"
          className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
          placeholder="Product Name (e.g., Quantum Laptop)"
          value={productName}
          onChange={(e) => setProductName(e.target.value)}
          disabled={isLoading}
        />
      </div>
      <button
        onClick={handleRunDiagnosis}
        className="mt-4 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300 disabled:opacity-50"
        disabled={isLoading}
      >
        {isLoading ? 'Running...' : 'Run Diagnosis'}
      </button>

      <div className="mt-6">
        <h3 className="text-xl font-semibold text-slate-200 mb-2">Diagnosis Report:</h3>
        <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 min-h-[100px] text-slate-300 font-mono text-sm">
          {isLoading && <p>Awaiting diagnosis...</p>}
          {error && <p className="text-red-400 whitespace-pre-wrap">{error}</p>}
          {report && <RenderReport report={report} />}
          {!isLoading && !error && !report && <p className="text-slate-500">The diagnosis report will appear here.</p>}
        </div>
      </div>
    </div>
  );
}

export default App;