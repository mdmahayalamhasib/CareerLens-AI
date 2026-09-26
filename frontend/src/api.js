const BASE_URL = 'http://127.0.0.1:8000';

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append('file', file); // Field name must match 'file' in FastAPI

  try {
    const response = await fetch(`${BASE_URL}/resume/upload`, {
      method: 'POST',
      body: formData,
      // Note: when using FormData, do not set Content-Type header. fetch will set it with boundary.
    });

    if (!response.ok) {
      // Try to parse the backend error detail
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
