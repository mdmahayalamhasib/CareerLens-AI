import { useState } from 'react';
import { analyzeJob } from '../api';
import JobMatchCard from '../components/JobMatchCard';

export default function JobMatcher({ resumeData, setLatestMatchScore, setGlobalJobData, setActiveNav }) {
  const [jobDescription, setJobDescription] = useState('');
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
    if (!jobDescription.trim()) {
      setError('Please enter a job description.');
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeJob(jobDescription, resumeData);
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

  return (
    <div className="resume-analysis-page">
      <header className="page-header">
        <h2>Job Matcher</h2>
        <p>Compare your resume with a target job description.</p>
      </header>

      <section className="card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <h3 style={{ margin: 0 }}>Job Description</h3>
          <span className="upload-help">{jobDescription.length} characters</span>
        </div>
        
        <textarea
          className="job-textarea"
          value={jobDescription}
          onChange={(e) => { setJobDescription(e.target.value); setError(null); }}
          placeholder="Paste the job description here..."
          disabled={loading}
          rows={10}
        />

        {error && <div className="error-message" style={{ marginTop: '1rem' }}>{error}</div>}

        <button 
          className="btn-primary" 
          style={{ marginTop: '1rem' }}
          onClick={handleAnalyze} 
          disabled={!jobDescription.trim() || loading}
        >
          {loading ? 'Analyzing job match...' : 'Analyze Job'}
        </button>
      </section>

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
