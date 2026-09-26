export default function WelcomeCard({ onAnalyzeClick }) {
  return (
    <section className="welcome-card card">
      <div className="welcome-content">
        <h2>Welcome to CareerLens AI</h2>
        <p>Analyze your resume, compare it with job opportunities, identify skill gaps, prepare for interviews, and create tailored cover letters.</p>
        <button className="btn-primary" onClick={onAnalyzeClick}>Analyze My Resume</button>
      </div>
    </section>
  );
}
