// utils/uploadToCloudinary.js
export async function uploadToCloudinary(base64Audio) {
    const response = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file: base64Audio }),
    });
  
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData?.error || 'Failed to upload audio');
    }
  
    const data = await response.json();
    return data.url;
  }
  