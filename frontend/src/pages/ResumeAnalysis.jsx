import { useState } from 'react';
import { uploadResume, analyzeResumeQuality } from '../api';
import ResumeQualityCard from '../components/ResumeQualityCard';

export default function ResumeAnalysis({ setGlobalAtsScore, setGlobalResumeData }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState('');
  const [error, setError] = useState(null);
  const [qualityError, setQualityError] = useState(null);
  
  const [result, setResult] = useState(null);
  const [qualityResult, setQualityResult] = useState(null);
  const [showRawText, setShowRawText] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError(null);
    setQualityError(null);
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().match(/\.(pdf|docx)$/)) {
      setError('Please upload a PDF or DOCX file.');
      setFile(null);
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError('File size must be 5 MB or less.');
      setFile(null);
      return;
    }

    setFile(selectedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setLoadingStep('Extracting resume information...');
    setError(null);
    setQualityError(null);
    setResult(null);
    setQualityResult(null);

    let parsedResumeData = null;

    // Step 1: Upload and Parse
    try {
      const data = await uploadResume(file);
      setResult(data);
      parsedResumeData = data.resume_data;
      if (setGlobalResumeData) setGlobalResumeData(parsedResumeData);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      return; // Stop flow if upload fails
    }

    // Step 2: Quality Analysis
    if (parsedResumeData) {
      setLoadingStep('Calculating ATS readiness...');
      try {
        const qualityData = await analyzeResumeQuality(parsedResumeData);
        setQualityResult(qualityData.quality_analysis);
        
        // Update dashboard state if provided
        if (setGlobalAtsScore && qualityData.quality_analysis) {
          setGlobalAtsScore(qualityData.quality_analysis.overall_score);
        }
      } catch (err) {
        setQualityError('Resume quality analysis could not be completed.');
      }
    }
    
    setLoading(false);
  };

  return (
    <div className="resume-analysis-page">
      <header className="page-header">
        <h2>Resume Analysis</h2>
        <p>Upload your resume to analyze its structure, skills, experience, and ATS readiness.</p>
      </header>

      <section className="upload-section card">
        <div className="upload-area">
          <h3>Upload your resume</h3>
          <p className="upload-help">PDF or DOCX, maximum 5 MB</p>
          
          <input 
            type="file" 
            id="resume-upload" 
            accept=".pdf,.docx" 
            onChange={handleFileChange}
            className="file-input"
            disabled={loading}
          />
          
          {file && !error && (
            <div className="file-info">
              <p><strong>Selected:</strong> {file.name}</p>
              <p><strong>Size:</strong> {(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          <button 
            className="btn-primary upload-btn" 
            onClick={handleUpload} 
            disabled={!file || loading}
          >
            {loading ? loadingStep : 'Analyze Resume'}
          </button>
        </div>
      </section>

      {result && result.resume_data && (
        <div className="analysis-results">
          
          {/* Quality Analysis Results */}
          {qualityResult && (
            <ResumeQualityCard 
              score={qualityResult.overall_score}
              readiness={qualityResult.ats_readiness}
              strengths={qualityResult.strengths}
              improvements={qualityResult.improvements}
              sectionStatus={qualityResult.section_status}
            />
          )}

          {qualityError && (
            <div className="card error-message" style={{marginBottom: '1.5rem', textAlign: 'center'}}>
              {qualityError}
            </div>
          )}

          <section className="card overview-card">
            <h3>Resume Overview</h3>
            <div className="overview-grid">
              <div className="overview-item">
                <span className="label">Name:</span> 
                <span className="value">{result.resume_data.name || 'Not provided'}</span>
              </div>
              <div className="overview-item">
                <span className="label">Email:</span> 
                <span className="value">{result.resume_data.email || 'Not provided'}</span>
              </div>
              <div className="overview-item">
                <span className="label">Phone:</span> 
                <span className="value">{result.resume_data.phone || 'Not provided'}</span>
              </div>
              <div className="overview-item">
                <span className="label">Location:</span> 
                <span className="value">{result.resume_data.location || 'Not provided'}</span>
              </div>
              <div className="overview-item">
                <span className="label">LinkedIn:</span> 
                <span className="value">{result.resume_data.linkedin || 'Not provided'}</span>
              </div>
              <div className="overview-item">
                <span className="label">GitHub:</span> 
                <span className="value">{result.resume_data.github || 'Not provided'}</span>
              </div>
            </div>
          </section>

          <section className="card">
            <h3>Skills</h3>
            <div className="skills-container">
              {(result.resume_data.skills || []).length > 0 ? (
                result.resume_data.skills.map((skill, index) => (
                  <span key={index} className="skill-badge">{skill}</span>
                ))
              ) : (
                <p>No skills detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Education</h3>
            <div className="list-container">
              {(result.resume_data.education || []).length > 0 ? (
                result.resume_data.education.map((edu, index) => (
                  <div key={index} className="list-item">
                    {typeof edu === 'string' ? edu : JSON.stringify(edu)}
                  </div>
                ))
              ) : (
                <p>No education detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Experience</h3>
            <div className="list-container">
              {(result.resume_data.experience || []).length > 0 ? (
                result.resume_data.experience.map((exp, index) => (
                  <div key={index} className="list-item">
                    {typeof exp === 'string' ? exp : JSON.stringify(exp)}
                  </div>
                ))
              ) : (
                <p>No experience detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Projects</h3>
            <div className="projects-container">
              {(result.resume_data.projects || []).length > 0 ? (
                result.resume_data.projects.map((proj, index) => (
                  <div key={index} className="project-item">
                    {typeof proj === 'string' ? (
                      <p>{proj}</p>
                    ) : (
                      <>
                        <h4>{proj.name || 'Unnamed Project'} {proj.year ? `(${proj.year})` : ''}</h4>
                        <div className="skills-container">
                          {(proj.technologies || []).map((tech, i) => (
                            <span key={i} className="skill-badge small">{tech}</span>
                          ))}
                        </div>
                        {proj.description && <p className="project-desc">{proj.description}</p>}
                      </>
                    )}
                  </div>
                ))
              ) : (
                <p>No projects detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Certifications</h3>
            <div className="list-container">
              {(result.resume_data.certifications || []).length > 0 ? (
                result.resume_data.certifications.map((cert, index) => (
                  <div key={index} className="list-item">{cert}</div>
                ))
              ) : (
                <p>No certifications detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Leadership</h3>
            <div className="list-container">
              {(result.resume_data.leadership || []).length > 0 ? (
                result.resume_data.leadership.map((item, index) => (
                  <div key={index} className="list-item">{item}</div>
                ))
              ) : (
                <p>No leadership experience detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <h3>Publications & Datasets</h3>
            <div className="list-container">
              {(result.resume_data.publications || []).length > 0 ? (
                result.resume_data.publications.map((item, index) => (
                  <div key={index} className="list-item">{item}</div>
                ))
              ) : (
                <p>No publications or datasets detected.</p>
              )}
            </div>
          </section>

          <section className="card">
            <div className="flex-between">
              <h3>Extracted Text</h3>
              <span>Extracted characters: {result.character_count || 0}</span>
            </div>
            <button className="btn-secondary toggle-btn" onClick={() => setShowRawText(!showRawText)}>
              {showRawText ? 'Hide Extracted Text' : 'View Extracted Text'}
            </button>
            
            {showRawText && (
              <div className="raw-text-container">
                <pre>{result.extracted_text}</pre>
              </div>
            )}
          </section>

        </div>
      )}
    </div>
  );
}
