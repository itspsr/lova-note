document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
  
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
  
      if (data.cloudinary_url) {
        // Display the Cloudinary URL and playback option
        document.getElementById('uploadResult').innerHTML = `
          <p>File uploaded successfully!</p>
          <p>Cloudinary URL: <a href="${data.cloudinary_url}" target="_blank">${data.cloudinary_url}</a></p>
          <audio id="audioPlayer" controls>
            <source src="${data.cloudinary_url}" type="audio/mpeg">
            Your browser does not support the audio element.
          </audio>
        `;
      } else {
        document.getElementById('uploadResult').innerHTML = `
          <p>Upload failed. Please try again.</p>
        `;
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      document.getElementById('uploadResult').innerHTML = `
        <p>There was an error with the upload. Please try again.</p>
      `;
    }
  });
  