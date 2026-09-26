export default function CareerRecommendations({ recommendations, summary }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Career Recommendations</h3>
        <p className="empty-list" style={{ marginTop: '0.5rem' }}>
          No career skill recommendations are needed because no skill gaps were identified.
        </p>
      </div>
    );
  }

  return (
    <div className="career-recommendations-section" style={{ marginTop: '2rem' }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
        Career Recommendations
      </h2>
      
      {summary && (
        <div className="card overview-card" style={{ marginBottom: '1.5rem' }}>
          <p>{summary}</p>
        </div>
      )}

      <div className="recommendations-grid">
        {recommendations.map((rec, index) => (
          <div key={index} className="card recommendation-card">
            <div className="flex-between" style={{ marginBottom: '1rem', alignItems: 'flex-start' }}>
              <h3 style={{ color: 'var(--primary-color)', margin: 0 }}>{rec.skill}</h3>
              <span className={`importance-badge ${rec.importance.toLowerCase()}`}>
                {rec.importance}
              </span>
            </div>
            
            <div className="rec-section">
              <h4>Why it matters</h4>
              <p>{rec.why_it_matters}</p>
            </div>
            
            <div className="rec-section">
              <h4>What to learn</h4>
              <p>{rec.what_to_learn}</p>
            </div>
            
            <div className="rec-section">
              <h4>Practice idea</h4>
              <p>{rec.practice_idea}</p>
            </div>
            
            {rec.project_idea && (
              <div className="rec-section">
                <h4>Project idea</h4>
                <p>{rec.project_idea}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
