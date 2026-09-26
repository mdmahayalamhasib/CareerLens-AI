export default function JobMatchCard({ score }) {
  if (score === null || score === undefined) {
    return (
      <div className="card ats-score-card">
        <h3>Match Score</h3>
        <div className="score-display">
          <span className="score-value">N/A</span>
          <span className="score-label">Not available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="card ats-score-card">
      <h3>Match Score</h3>
      <div className="score-display">
        <span className="score-value">{score}%</span>
        <span className="score-label">Match Score</span>
      </div>
    </div>
  );
}
