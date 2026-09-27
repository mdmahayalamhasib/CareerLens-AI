export default function InterviewSummary({ summary }) {
  if (!summary) return null;

  return (
    <div className="interview-summary-section" style={{ marginTop: '2rem' }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
        Interview Summary
      </h2>
      
      <div className="stats-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="card stat-card" style={{ textAlign: 'center' }}>
          <span className="stat-value" style={{ color: 'var(--primary-color)' }}>{summary.overall_score || 0} / 10</span>
          <span className="stat-label">Overall Score</span>
        </div>
        <div className="card stat-card" style={{ textAlign: 'center' }}>
          <span className="stat-value">{summary.answered_questions} / {summary.total_questions}</span>
          <span className="stat-label">Questions Answered</span>
        </div>
        <div className="card stat-card" style={{ textAlign: 'center' }}>
          <span className="stat-value">{summary.average_score?.toFixed(1) || 0}</span>
          <span className="stat-label">Average Score</span>
        </div>
      </div>

      <div className="card overview-card" style={{ marginBottom: '1.5rem' }}>
        <h3 style={{ marginBottom: '0.5rem' }}>Recommendation</h3>
        <p>{summary.recommendation}</p>
      </div>

      <div className="recommendations-grid">
        <div className="card">
          <h3>Top Strengths</h3>
          <div className="list-container">
            {summary.strengths && summary.strengths.length > 0 ? (
              <ul className="strength-list">
                {summary.strengths.map((str, idx) => (
                  <li key={idx}>✓ {str}</li>
                ))}
              </ul>
            ) : (
              <p className="empty-list">No significant strengths identified.</p>
            )}
          </div>
        </div>
        
        <div className="card">
          <h3>Areas to Improve</h3>
          <div className="list-container">
            {summary.areas_to_improve && summary.areas_to_improve.length > 0 ? (
              <ul className="improvement-list">
                {summary.areas_to_improve.map((imp, idx) => (
                  <li key={idx}>• {imp}</li>
                ))}
              </ul>
            ) : (
              <p className="empty-list">No major areas for improvement identified.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
