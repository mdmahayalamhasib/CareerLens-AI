import { useState } from 'react';

export default function CoverLetterCard({ coverLetterText, summary, skillsHighlighted, templateUsed }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(coverLetterText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card" style={{ marginTop: '2rem' }}>
      <div className="flex-between" style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
        <h3 style={{ margin: 0, color: 'var(--primary-color)' }}>Generated Cover Letter</h3>
        <button className="btn-secondary" onClick={handleCopy}>
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
      </div>
      
      {summary && (
        <div style={{ marginBottom: '1.5rem', padding: '0.75rem', backgroundColor: '#f1f5f9', borderRadius: '6px' }}>
          <p style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>
            <strong>Summary:</strong> {summary}
          </p>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            <strong>Template used:</strong> {templateUsed || 'Generic'}
          </p>
        </div>
      )}

      {skillsHighlighted && skillsHighlighted.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Skills Highlighted</h4>
          <div className="skills-container">
            {skillsHighlighted.map((skill, idx) => (
              <span key={idx} className="skill-badge small">{skill}</span>
            ))}
          </div>
        </div>
      )}

      <div style={{ 
        backgroundColor: '#f8fafc', 
        border: '1px solid #e2e8f0', 
        borderRadius: '6px', 
        padding: '1.5rem',
        whiteSpace: 'pre-wrap',
        fontFamily: 'inherit',
        lineHeight: '1.6',
        color: '#1e293b'
      }}>
        {coverLetterText}
      </div>
    </div>
  );
}
