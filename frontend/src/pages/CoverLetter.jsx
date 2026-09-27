import { useState } from 'react';
import { generateCoverLetter } from '../api';
import CoverLetterCard from '../components/CoverLetterCard';

export default function CoverLetter({ resumeData, jobData, setActiveNav }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!resumeData || !jobData) {
    return (
      <div className="resume-analysis-page">
        <header className="page-header">
          <h2>Cover Letter Generator</h2>
          <p>Create a tailored, professional cover letter based on your resume and target job.</p>
        </header>
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Missing Information</h3>
          <p className="upload-help" style={{ marginBottom: '1.5rem' }}>
            Cover letter generation requires both an analyzed resume and a matched job description.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn-secondary" onClick={() => setActiveNav('resume')}>
              Go to Resume Analysis
            </button>
            <button className="btn-primary" onClick={() => setActiveNav('job')}>
              Go to Job Matcher
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await generateCoverLetter(resumeData, jobData);
      if (data && data.cover_letter) {
        setResult(data);
      } else {
        setError('Received an empty response from the server.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="resume-analysis-page">
      <header className="page-header">
        <div className="flex-between">
          <div>
            <h2>Cover Letter Generator</h2>
            <p>Create a tailored, professional cover letter based on your resume and target job.</p>
          </div>
        </div>
      </header>

      {error && <div className="card error-message" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>{error}</div>}

      {!result && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Ready to Generate?</h3>
          <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>
            We will use your analyzed resume and the target job description to draft a tailored cover letter.
          </p>
          <button className="btn-primary" onClick={handleGenerate}>
            Generate Cover Letter
          </button>
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ fontSize: '1.125rem', color: 'var(--primary-color)' }}>Drafting your professional cover letter...</p>
        </div>
      )}

      {result && !loading && (
        <div className="cover-letter-results">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', marginBottom: '1rem' }}>
            <h3 style={{ color: '#166534', margin: 0 }}>Cover Letter Ready!</h3>
          </div>
          
          <CoverLetterCard 
            coverLetterText={result.cover_letter}
            summary={result.summary}
            skillsHighlighted={result.matched_skills_highlighted}
            templateUsed={result.template_used}
          />
          
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
            <button className="btn-secondary" onClick={handleGenerate}>
              Regenerate Letter
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
