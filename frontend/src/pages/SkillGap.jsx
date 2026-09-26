import { useState, useEffect } from 'react';
import { analyzeSkillGap, getCareerRecommendations } from '../api';
import CareerRecommendations from '../components/CareerRecommendations';

export default function SkillGap({ resumeData, jobData, setGlobalSkillsToImprove, setActiveNav }) {
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);
  const [gapResult, setGapResult] = useState(null);
  const [recResult, setRecResult] = useState(null);

  if (!resumeData || !jobData) {
    return (
      <div className="resume-analysis-page">
        <header className="page-header">
          <h2>Skill Gap Analysis</h2>
          <p>Identify the skills you need to improve for your target job.</p>
        </header>
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Missing Information</h3>
          <p className="upload-help" style={{ marginBottom: '1.5rem' }}>
            Skill Gap Analysis requires both an analyzed resume and a matched job description.
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

  const runAnalysis = async () => {
    setLoading(true);
    setLoadingStep('Analyzing skill gaps...');
    setError(null);
    setGapResult(null);
    setRecResult(null);

    try {
      // Step 1: Analyze Gaps
      const gapData = await analyzeSkillGap(resumeData, jobData);
      setGapResult(gapData);

      // Store in dashboard stat
      if (setGlobalSkillsToImprove) {
        setGlobalSkillsToImprove(gapData.skill_gaps.length);
      }

      // Step 2: Get Recommendations if there are gaps
      if (gapData.skill_gaps && gapData.skill_gaps.length > 0) {
        setLoadingStep('Generating career recommendations...');
        const recData = await getCareerRecommendations(gapData.skill_gaps);
        setRecResult(recData);
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
            <h2>Skill Gap Analysis</h2>
            <p>Identify the skills you need to improve for your target job.</p>
          </div>
          <button 
            className="btn-primary" 
            onClick={runAnalysis} 
            disabled={loading}
          >
            {loading ? loadingStep : 'Run Analysis'}
          </button>
        </div>
      </header>

      {error && <div className="card error-message" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>{error}</div>}

      {gapResult && (
        <div className="analysis-results">
          
          <div className="resume-quality-card">
            <div className="card ats-score-card">
              <h3>Required Coverage</h3>
              <div className="score-display">
                <span className="score-value">{gapResult.required_skill_coverage}%</span>
                <span className="score-label">Coverage</span>
              </div>
            </div>

            <div className="card ats-score-card" style={{ background: 'linear-gradient(135deg, #f8fafc, #f1f5f9)', borderColor: '#cbd5e1' }}>
              <h3 style={{ color: '#475569' }}>Preferred Coverage</h3>
              <div className="score-display">
                <span className="score-value" style={{ color: '#475569' }}>{gapResult.preferred_skill_coverage}%</span>
                <span className="score-label">Coverage</span>
              </div>
            </div>
          </div>

          <div className="resume-quality-card" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="card">
              <h3>Matched Required Skills</h3>
              <div className="skills-container">
                {gapResult.matched_required_skills && gapResult.matched_required_skills.length > 0 ? (
                  gapResult.matched_required_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge">{skill}</span>
                  ))
                ) : (
                  <p className="empty-list">No required skills matched.</p>
                )}
              </div>
            </div>
            <div className="card">
              <h3>Matched Preferred Skills</h3>
              <div className="skills-container">
                {gapResult.matched_preferred_skills && gapResult.matched_preferred_skills.length > 0 ? (
                  gapResult.matched_preferred_skills.map((skill, idx) => (
                    <span key={idx} className="skill-badge" style={{ backgroundColor: '#f1f5f9', color: '#64748b' }}>{skill}</span>
                  ))
                ) : (
                  <p className="empty-list">No preferred skills matched.</p>
                )}
              </div>
            </div>
          </div>

          <section className="card">
            <h3>Skill Gaps</h3>
            {gapResult.summary && <p style={{ marginTop: '0.5rem', marginBottom: '1.5rem' }}>{gapResult.summary}</p>}
            
            <div className="projects-container">
              {gapResult.skill_gaps && gapResult.skill_gaps.length > 0 ? (
                gapResult.skill_gaps.map((gap, index) => (
                  <div key={index} className="project-item">
                    <div className="flex-between" style={{ marginBottom: '0.5rem', alignItems: 'flex-start' }}>
                      <h4 style={{ margin: 0, color: '#ef4444' }}>{gap.skill}</h4>
                      <span className={`importance-badge ${gap.importance.toLowerCase()}`}>
                        {gap.importance}
                      </span>
                    </div>
                    <p className="project-desc">{gap.reason}</p>
                  </div>
                ))
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: '#f0fdf4', borderRadius: '6px', border: '1px dashed #bbf7d0' }}>
                  <p style={{ color: '#166534', fontWeight: '500' }}>No skill gaps were identified for this job.</p>
                </div>
              )}
            </div>
          </section>

          {/* Render Career Recommendations if gaps exist and we have the result */}
          {gapResult.skill_gaps && gapResult.skill_gaps.length > 0 ? (
             recResult && (
               <CareerRecommendations 
                 recommendations={recResult.recommendations} 
                 summary={recResult.summary} 
               />
             )
          ) : (
             <CareerRecommendations recommendations={[]} summary={null} />
          )}

        </div>
      )}
    </div>
  );
}
