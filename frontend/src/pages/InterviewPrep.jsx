import { useState } from 'react';
import { generateInterviewQuestions, evaluateInterviewAnswer, getInterviewSummary } from '../api';
import InterviewQuestionCard from '../components/InterviewQuestionCard';
import InterviewSummary from '../components/InterviewSummary';

export default function InterviewPrep({ resumeData, jobData, setActiveNav }) {
  const [questions, setQuestions] = useState([]);
  const [evaluations, setEvaluations] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [summary, setSummary] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);
  
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);

  if (!resumeData || !jobData) {
    return (
      <div className="resume-analysis-page">
        <header className="page-header">
          <h2>Interview Preparation</h2>
          <p>Practice with AI-generated interview questions tailored to your target job.</p>
        </header>
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Missing Information</h3>
          <p className="upload-help" style={{ marginBottom: '1.5rem' }}>
            Interview preparation requires both an analyzed resume and a matched job description.
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

  const startInterview = async () => {
    setLoading(true);
    setLoadingStep('Generating tailored interview questions...');
    setError(null);
    setQuestions([]);
    setEvaluations([]);
    setCurrentIdx(0);
    setSummary(null);
    setInterviewCompleted(false);

    try {
      const data = await generateInterviewQuestions(jobData, resumeData);
      if (data.questions && data.questions.length > 0) {
        setQuestions(data.questions);
        setInterviewStarted(true);
      } else {
        setError('No questions were generated. Please try again or check your job description.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleEvaluateAnswer = async (answer) => {
    setLoading(true);
    setError(null);
    const currentQ = questions[currentIdx];

    try {
      const data = await evaluateInterviewAnswer(currentQ, answer);
      const evalData = data.evaluation;
      
      const updatedEvaluations = [...evaluations, evalData];
      setEvaluations(updatedEvaluations);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    } else {
      // Finish interview
      setLoading(true);
      setLoadingStep('Generating interview summary...');
      try {
        const data = await getInterviewSummary(evaluations);
        setSummary(data.summary);
        setInterviewCompleted(true);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="resume-analysis-page">
      <header className="page-header">
        <h2>Interview Preparation</h2>
        <p>Practice with AI-generated interview questions tailored to your target job.</p>
      </header>

      {error && <div className="card error-message" style={{ marginBottom: '1.5rem', textAlign: 'center' }}>{error}</div>}

      {!interviewStarted && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3>Ready to Practice?</h3>
          <p style={{ marginBottom: '1.5rem', color: 'var(--text-muted)' }}>
            We will generate technical, project-based, and behavioral questions tailored specifically to your resume and the target job description.
          </p>
          <button className="btn-primary" onClick={startInterview}>
            Start Interview Preparation
          </button>
        </div>
      )}

      {loading && !interviewStarted && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ fontSize: '1.125rem', color: 'var(--primary-color)' }}>{loadingStep}</p>
        </div>
      )}

      {interviewStarted && !interviewCompleted && (
        <div className="interview-session">
          <InterviewQuestionCard 
            question={questions[currentIdx]}
            currentIdx={currentIdx}
            total={questions.length}
            onEvaluate={handleEvaluateAnswer}
            evaluation={evaluations[currentIdx]} // Pass evaluation if it exists for the current question
            loading={loading}
          />

          {evaluations[currentIdx] && (
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn-primary" onClick={handleNext} disabled={loading}>
                {currentIdx < questions.length - 1 ? 'Next Question' : 'Finish Interview'}
              </button>
            </div>
          )}
        </div>
      )}

      {interviewCompleted && summary && (
        <div className="interview-results">
          <div className="card" style={{ textAlign: 'center', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', marginBottom: '2rem' }}>
            <h3 style={{ color: '#166534', margin: 0 }}>Interview Practice Completed!</h3>
          </div>
          
          <InterviewSummary summary={summary} />
          
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
            <button className="btn-secondary" onClick={startInterview}>
              Start a New Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
