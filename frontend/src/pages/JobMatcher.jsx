import { useState } from 'react';
import { analyzeJob, analyzeJobPdf } from '../api';
import JobMatchCard from '../components/JobMatchCard';

export default function JobMatcher({ resumeData, setLatestMatchScore, setGlobalJobData, setActiveNav }) {
  const [jobDescription, setJobDescription] = useState('');
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  if (!resumeData) {
    return (
      <div className="resume-analysis-page">
        <header className="page-header">
          <h2>Job Matcher</h2>
          <p>Compare your resume with a target job description.</p>
        </header>
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Please analyze your resume first.</h3>
          <p className="upload-help" style={{ marginBottom: '1.5rem' }}>
            Job matching requires an analyzed resume to compare against.
          </p>
          <button className="btn-primary" onClick={() => setActiveNav('resume')}>
            Go to Resume Analysis
          </button>
        </div>
      </div>
    );
  }

  const handleAnalyze = async () => {
    if (!jobDescription.trim() && !pdfFile) {
      setError('Please enter a job description or upload a PDF.');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let data;
      if (pdfFile) {
        data = await analyzeJobPdf(pdfFile, resumeData);
      } else {
        data = await analyzeJob(jobDescription, resumeData);
      }

      setResult(data);
      if (setLatestMatchScore && data.match) {
        setLatestMatchScore(data.match.match_score);
      }
      if (setGlobalJobData && data.job) {
        setGlobalJobData(data.job);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Only PDF files are supported for Job Description uploads.');
        e.target.value = null;
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setError('File is too large. Maximum size is 5MB.');
        e.target.value = null;
        return;
      }
      setPdfFile(file);
      setJobDescription('');
      setError(null);
    }
  };


  return (
    <div className="resume-analysis-page">
      <header className="page-header">
        <h2>Job Matcher</h2>
        <p>Compare your resume with a target job description.</p>
      </header>

      <section className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>Provide Job Description</h3>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '1.5rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <label style={{ fontWeight: '600' }}>Paste Text</label>
              <span className="upload-help">{jobDescription.length} characters</span>
            </div>
            <textarea
              className="job-textarea"
              value={jobDescription}
              onChange={(e) => { setJobDescription(e.target.value); setPdfFile(null); setError(null); }}
              placeholder="Paste the job description here..."
              disabled={loading}
              rows={6}
            />
          </div>

          <div style={{ textAlign: 'center', fontWeight: 'bold', color: 'var(--text-muted)' }}>
            OR
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600' }}>Upload Job Description PDF</label>
            <div style={{ border: '2px dashed var(--border-color)', borderRadius: '6px', padding: '1.5rem', textAlign: 'center', backgroundColor: '#f8fafc' }}>
               <input 
                 type="file" 
                 accept=".pdf" 
                 onChange={handleFileChange}
                 disabled={loading}
                 style={{ maxWidth: '100%' }}
               />
               {pdfFile && <p style={{ marginTop: '0.75rem', color: 'var(--primary-color)', fontWeight: '600' }}>Selected file: {pdfFile.name}</p>}
            </div>
          </div>

        </div>

        {error && <div className="error-message" style={{ marginTop: '1rem', marginBottom: '1rem' }}>{error}</div>}

        <button 
          className="btn-primary" 
          onClick={handleAnalyze} 
          disabled={(!jobDescription.trim() && !pdfFile) || loading}
        >
          {loading ? 'Analyzing job match...' : 'Analyze Job'}
        </button>
      </section>
      
      {result && result.extracted_text && (
        <section className="card" style={{ marginBottom: '2rem', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0' }}>
          <h3 style={{ color: '#166534', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>✓</span> Job description extracted successfully
          </h3>
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'white', borderRadius: '4px', border: '1px solid #e2e8f0', maxHeight: '200px', overflowY: 'auto', whiteSpace: 'pre-wrap', fontSize: '0.9rem', color: '#334155' }}>
            {result.extracted_text}
          </div>
        </section>
      )}

      {result && result.match && result.job && (
        <div className="analysis-results">
          <div className="resume-quality-card">
            <JobMatchCard score={result.match.match_score} />
            
            <div className="card">
              <h3>Matched Skills</h3>
              <div className="skills-container">
                {result.match.matched_skills && result.match.matched_skills.length > 0 ? (
                  result.match.matched_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge">{skill}</span>
                  ))
                ) : (
                  <p className="empty-list">No matching required skills found.</p>
                )}
              </div>
            </div>

            <div className="card">
              <h3>Missing Skills</h3>
              <div className="skills-container">
                {result.match.missing_skills && result.match.missing_skills.length > 0 ? (
                  result.match.missing_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge" style={{ backgroundColor: '#fee2e2', color: '#ef4444' }}>{skill}</span>
                  ))
                ) : (
                  <p className="empty-list">No missing required skills.</p>
                )}
              </div>
            </div>
          </div>

          {result.transferable_evidence && result.transferable_evidence.length > 0 && (
            <section className="card" style={{ marginBottom: '2rem', backgroundColor: '#f8fafc', borderLeft: '4px solid #3b82f6' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#1e40af' }}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
                Transferable Evidence
              </h3>
              <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '1.5rem', fontStyle: 'italic' }}>
                Transferable evidence indicates potentially relevant experience. It does not confirm that the missing skill is present.
              </p>
              <div className="list-container">
                {result.transferable_evidence.map((evidence, idx) => {
                  let badgeText = "Not Relevant";
                  let badgeColor = "#94a3b8";
                  let badgeBg = "#f1f5f9";
                  
                  if (evidence.classification === 'transferable') {
                    badgeText = "Potentially Transferable";
                    badgeColor = "#047857";
                    badgeBg = "#d1fae5";
                  } else if (evidence.classification === 'related_but_not_equivalent') {
                    badgeText = "Related, but Not Equivalent";
                    badgeColor = "#b45309";
                    badgeBg = "#fef3c7";
                  }

                  const scorePct = evidence.relevance_score != null ? Math.round(evidence.relevance_score * 100) : 0;
                  
                  return (
                    <div key={idx} className="list-item" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', padding: '1.25rem', backgroundColor: 'white', border: '1px solid #e2e8f0', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem' }}>
                        <div>
                          <strong style={{ fontSize: '1.1rem', color: '#0f172a' }}>Missing Skill: {evidence.skill || 'Unknown'}</strong>
                          <div style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: '600' }}>
                            Source: {evidence.source_type || 'Resume'} - {evidence.source_title || 'Untitled'}
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#475569' }}>
                            Relevance: {scorePct}%
                          </span>
                          <span style={{ backgroundColor: badgeBg, color: badgeColor, padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.8rem', fontWeight: '600', whiteSpace: 'nowrap' }}>
                            {badgeText}
                          </span>
                        </div>
                      </div>
                      <p style={{ marginTop: '0.5rem', color: '#334155', lineHeight: '1.5' }}>
                        "{evidence.evidence_text || 'No description available.'}"
                      </p>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          <section className="card">
            <h3>Match Summary</h3>
            <p style={{ marginTop: '0.5rem', lineHeight: '1.6' }}>{result.match.summary}</p>
          </section>

          <section className="card">
            <h3>Relevant Projects</h3>
            <div className="list-container" style={{ marginTop: '1rem' }}>
              {result.match.relevant_projects && result.match.relevant_projects.length > 0 ? (
                result.match.relevant_projects.map((proj, index) => (
                  <div key={index} className="list-item">
                    {typeof proj === 'string' ? proj : JSON.stringify(proj)}
                  </div>
                ))
              ) : (
                <p className="empty-list">No directly relevant projects were identified.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Relevant Experience</h3>
            <div className="list-container" style={{ marginTop: '1rem' }}>
              {result.match.relevant_experience && result.match.relevant_experience.length > 0 ? (
                result.match.relevant_experience.map((exp, index) => (
                  <div key={index} className="list-item">
                    {typeof exp === 'string' ? exp : JSON.stringify(exp)}
                  </div>
                ))
              ) : (
                <p className="empty-list">No directly relevant experience was identified.</p>
              )}
            </div>
          </section>

          <h2 style={{ marginTop: '1rem', marginBottom: '1rem', fontSize: '1.25rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
            Job Analysis
          </h2>

          <section className="card overview-card">
            <h3>Job Overview</h3>
            <div className="overview-grid">
              <div className="overview-item">
                <span className="label">Job Title:</span> 
                <span className="value">{result.job.job_title || 'No information detected.'}</span>
              </div>
              <div className="overview-item">
                <span className="label">Experience Requirements:</span> 
                <span className="value">{result.job.experience_requirements || 'No information detected.'}</span>
              </div>
            </div>
          </section>

          <section className="card">
            <h3>Required Skills</h3>
            <div className="skills-container">
              {result.job.required_skills && result.job.required_skills.length > 0 ? (
                result.job.required_skills.map((skill, idx) => (
                  <span key={idx} className="skill-badge">{skill}</span>
                ))
              ) : (
                <p className="empty-list">No information detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Preferred Skills</h3>
            <div className="skills-container">
              {result.job.preferred_skills && result.job.preferred_skills.length > 0 ? (
                result.job.preferred_skills.map((skill, idx) => (
                  <span key={idx} className="skill-badge" style={{ backgroundColor: '#f1f5f9', color: '#64748b' }}>{skill}</span>
                ))
              ) : (
                <p className="empty-list">No information detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Responsibilities</h3>
            <div className="list-container">
              {result.job.responsibilities && result.job.responsibilities.length > 0 ? (
                result.job.responsibilities.map((req, idx) => (
                  <div key={idx} className="list-item">• {req}</div>
                ))
              ) : (
                <p className="empty-list">No information detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Qualifications</h3>
            <div className="list-container">
              {result.job.qualifications && result.job.qualifications.length > 0 ? (
                result.job.qualifications.map((qual, idx) => (
                  <div key={idx} className="list-item">• {qual}</div>
                ))
              ) : (
                <p className="empty-list">No information detected.</p>
              )}
            </div>
          </section>

        </div>
      )}
    </div>
  );
}
