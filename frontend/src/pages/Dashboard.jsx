import WelcomeCard from '../components/WelcomeCard';
import StatCard from '../components/StatCard';
import ToolCard from '../components/ToolCard';
import RecentActivity from '../components/RecentActivity';

export default function Dashboard({ setActiveNav, atsScore, latestMatchScore }) {
  return (
    <div className="dashboard-content">
      <WelcomeCard onAnalyzeClick={() => setActiveNav('resume')} />
      
      <section className="stats-grid">
        <StatCard value={atsScore !== null ? atsScore : "--"} label="ATS Readiness" />
        <StatCard value={latestMatchScore !== null ? `${latestMatchScore}%` : "N/A"} label="Latest Match" />
        <StatCard value="--" label="Skills to Improve" />
        <StatCard value="--" label="Latest Session" />
      </section>
      
      <section className="tools-section">
        <h2>Career Tools</h2>
        <div className="tools-grid">
          <ToolCard 
            title="Resume Analysis" 
            description="Check your resume structure, quality, and ATS readiness." 
            buttonText="Analyze Resume" 
            onClick={() => setActiveNav('resume')}
          />
          <ToolCard 
            title="Job Matcher" 
            description="Compare your resume with a job description and identify matching and missing skills." 
            buttonText="Match a Job" 
            onClick={() => setActiveNav('job')}
          />
          <ToolCard 
            title="Skill Gap Advisor" 
            description="Find the skills you need to improve for your target role." 
            buttonText="Explore Skills" 
          />
          <ToolCard 
            title="Interview Prep" 
            description="Practice interview questions and evaluate your answers." 
            buttonText="Start Practice" 
          />
          <ToolCard 
            title="Cover Letter" 
            description="Create a tailored cover letter based on your resume and target job." 
            buttonText="Create Letter" 
          />
        </div>
      </section>
      
      <RecentActivity />
    </div>
  );
}
