import { useState, useEffect } from 'react';

export default function InterviewQuestionCard({ question, currentIdx, total, onEvaluate, evaluation, loading }) {
  const [answer, setAnswer] = useState('');

  // Clear textarea when the question index changes
  useEffect(() => {
    setAnswer('');
  }, [currentIdx]);

  const handleSubmit = () => {
    if (!answer.trim()) return;
    onEvaluate(answer);
  };

  return (
    <div className="card" style={{ marginBottom: '2rem' }}>
      <div className="flex-between" style={{ marginBottom: '1rem' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>
          Question {currentIdx + 1} of {total}
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <span className="importance-badge" style={{ backgroundColor: '#e0e7ff', color: '#4338ca' }}>
            {question.type}
          </span>
          {question.skill && (
            <span className="skill-badge small">{question.skill}</span>
          )}
        </div>
      </div>
      
      <h3 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>{question.question}</h3>
      
      {/* Textarea is always rendered, disabled if evaluating or already evaluated */}
      <textarea
        className="job-textarea"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
        placeholder="Type your answer here..."
        disabled={loading || !!evaluation}
        rows={6}
        style={{ marginBottom: '1rem' }}
      />

      {!evaluation ? (
        <button 
          className="btn-primary" 
          onClick={handleSubmit} 
          disabled={!answer.trim() || loading}
        >
          {loading ? 'Evaluating...' : 'Submit Answer'}
        </button>
      ) : (
        <div className="evaluation-result" style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
          <div className="flex-between" style={{ marginBottom: '1rem' }}>
            <h4>Evaluation Result</h4>
            <span className="score-value" style={{ fontSize: '1.5rem', color: 'var(--primary-color)' }}>
              {evaluation.score} / 10
            </span>
          </div>
          
          <p style={{ marginBottom: '1.5rem', lineHeight: '1.5' }}><strong>Feedback:</strong> {evaluation.feedback}</p>
          
          <div className="recommendations-grid">
            <div className="card" style={{ padding: '1rem' }}>
              <h4 style={{ fontSize: '0.95rem' }}>Strengths</h4>
              {evaluation.strengths && evaluation.strengths.length > 0 ? (
                <ul className="strength-list" style={{ marginTop: '0.5rem' }}>
                  {evaluation.strengths.map((str, idx) => (
                    <li key={idx}>✓ {str}</li>
                  ))}
                </ul>
              ) : (
                <p className="empty-list">No specific strengths identified.</p>
              )}
            </div>
            <div className="card" style={{ padding: '1rem' }}>
              <h4 style={{ fontSize: '0.95rem' }}>Improvements</h4>
              {evaluation.improvements && evaluation.improvements.length > 0 ? (
                <ul className="improvement-list" style={{ marginTop: '0.5rem' }}>
                  {evaluation.improvements.map((imp, idx) => (
                    <li key={idx}>• {imp}</li>
                  ))}
                </ul>
              ) : (
                <p className="empty-list">No specific improvements identified.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
