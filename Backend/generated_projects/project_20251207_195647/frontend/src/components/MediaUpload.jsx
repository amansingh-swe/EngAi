import React, { useState } from 'react';
import api from '../services/api';

function MediaUpload() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
      setMessage('');
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setMessage('Uploading...');
    setError('');
    try {
      const response = await api.uploadMedia(file);
      setMessage(`File uploaded successfully! URL: ${response.media_url}`);
      setFile(null);
      setPreviewUrl('');
      // Optionally clear the file input
      document.getElementById('mediaFile').value = '';
    } catch (err) {
      setError(err.message);
      setMessage('');
    }
  };

  return (
    <div className="form-container">
      <h2 className="form-title">Upload Media</h2>
      {error && <p className="error-message">{error}</p>}
      {message && <p className="success-message">{message}</p>}
      <div className="form-group">
        <label htmlFor="mediaFile" className="form-label">Choose File</label>
        <input
          type="file"
          id="mediaFile"
          className="form-input"
          onChange={handleFileChange}
        />
      </div>
      {previewUrl && (
        <div className="media-upload-preview">
          <p>Preview:</p>
          <img src={previewUrl} alt="Media Preview" style={{ maxWidth: '300px', height: 'auto', marginTop: '10px' }} />
        </div>
      )}
      <button onClick={handleUpload} className="form-button" disabled={!file}>
        {message === 'Uploading...' ? 'Uploading...' : 'Upload Media'}
      </button>
    </div>
  );
}

export default MediaUpload;