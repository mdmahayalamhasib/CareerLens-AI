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
