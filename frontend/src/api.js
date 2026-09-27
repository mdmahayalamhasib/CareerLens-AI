const BASE_URL = 'http://127.0.0.1:8000';

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${BASE_URL}/resume/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during upload.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Unable to connect to the CareerLens AI backend. Please make sure the FastAPI server is running.');
    }
    throw error;
  }
}

export async function analyzeResumeQuality(resumeData) {
  try {
    const response = await fetch(`${BASE_URL}/resume/quality`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_data: resumeData }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during quality analysis.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Unable to connect to the CareerLens AI backend. Please make sure the FastAPI server is running.');
    }
    throw error;
  }
}

export async function analyzeJob(jobDescription, resumeData) {
  try {
    const response = await fetch(`${BASE_URL}/job/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_description: jobDescription, resume_data: resumeData }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during job analysis.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Unable to connect to the CareerLens AI backend. Please make sure the FastAPI server is running.');
    }
    throw error;
  }
}

export async function analyzeSkillGap(resumeData, jobData) {
  try {
    const response = await fetch(`${BASE_URL}/skills/gap-analysis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_data: resumeData, job_data: jobData }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during skill gap analysis.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Unable to connect to the CareerLens AI backend. Please make sure the FastAPI server is running.');
    }
    throw error;
  }
}

export async function getCareerRecommendations(skillGaps) {
  try {
    const response = await fetch(`${BASE_URL}/career/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skill_gaps: skillGaps }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred while fetching career recommendations.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      throw new Error('Unable to connect to the CareerLens AI backend. Please make sure the FastAPI server is running.');
    }
    throw error;
  }
}

export async function generateInterviewQuestions(jobData, resumeData) {
  try {
    const response = await fetch(`${BASE_URL}/interview/questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_data: jobData, resume_data: resumeData }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during question generation.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status}`;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') throw new Error('Unable to connect to the backend.');
    throw error;
  }
}

export async function evaluateInterviewAnswer(question, answer) {
  try {
    const response = await fetch(`${BASE_URL}/interview/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during evaluation.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status}`;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') throw new Error('Unable to connect to the backend.');
    throw error;
  }
}

export async function getInterviewSummary(evaluations) {
  try {
    const response = await fetch(`${BASE_URL}/interview/summary`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ evaluations }),
    });

    if (!response.ok) {
      let errorMessage = 'An error occurred during summary generation.';
      try {
        const errData = await response.json();
        errorMessage = errData.detail || errorMessage;
      } catch (e) {
        errorMessage = `HTTP Error: ${response.status}`;
      }
      throw new Error(errorMessage);
    }
    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') throw new Error('Unable to connect to the backend.');
    throw error;
  }
}
