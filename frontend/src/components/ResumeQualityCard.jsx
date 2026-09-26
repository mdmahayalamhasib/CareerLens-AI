export default function ResumeQualityCard({ score, readiness, strengths, improvements, sectionStatus }) {
  if (score === null || score === undefined) {
    return (
      <div className="card">
        <h3>ATS Readiness</h3>
        <p>Not available</p>
      </div>
    );
  }

  return (
    <div className="resume-quality-card">
      <div className="card ats-score-card">
        <h3>ATS Readiness</h3>
        <div className="score-display">
          <span className="score-value">{score} / 100</span>
          <span className="score-label">{readiness || 'Unknown'}</span>
          <span className="score-heuristic">ATS Readiness Heuristic</span>
        </div>
      </div>

      <div className="card strengths-card">
        <h3>Resume Strengths</h3>
        {strengths && strengths.length > 0 ? (
          <ul className="strength-list">
            {strengths.map((str, idx) => (
              <li key={idx}>✓ {str}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-list">No specific strengths identified.</p>
        )}
      </div>

      <div className="card improvements-card">
        <h3>Recommended Improvements</h3>
        {improvements && improvements.length > 0 ? (
          <ul className="improvement-list">
            {improvements.map((imp, idx) => (
              <li key={idx}>• {imp}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-list">No specific improvements identified.</p>
        )}
      </div>
      
      {/* 
        The prompt mentioned to render score breakdown if available. 
        Based on backend inspection, there are no individual section scores (just section_status booleans). 
        So we don't render a numeric breakdown because it's not provided by the backend.
      */}
    </div>
  );
}
