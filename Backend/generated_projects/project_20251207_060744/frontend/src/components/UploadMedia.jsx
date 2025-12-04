import React, { useState } from 'react';
import { apiService } from '../services/api';

function UploadMedia() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedUrl, setUploadedUrl] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setUploadedUrl(''); // Clear previous URL on new file selection
    setError('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setError('');
    setUploadedUrl('');

    try {
      // The API service needs to be configured to handle multipart/form-data
      // The `request` function in api.js already handles this if 'Content-Type' is not explicitly set to 'application/json'
      // or if we explicitly set it to 'multipart/form-data' for this specific call.
      // Let's ensure the apiService.uploadMedia handles this.
      const response = await apiService.uploadMedia(formData);
      setUploadedUrl(response.media_url);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div>
      <h2>Upload Media</h2>
      <div>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={!selectedFile}>Upload</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {uploadedUrl && (
        <div>
          <p>File uploaded successfully!</p>
          <p>Media URL: <a href={uploadedUrl} target="_blank" rel="noopener noreferrer">{uploadedUrl}</a></p>
          <img src={uploadedUrl} alt="Uploaded Media" style={{ maxWidth: '300px', maxHeight: '300px', marginTop: '10px' }} />
        </div>
      )}
    </div>
  );
}

export default UploadMedia;