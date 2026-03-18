import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// Predict emotion from Face Image
export const predictFromImage = async (file, mode = 'match') => {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('mode', mode);
  
  const response = await api.post('/predict/image/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// Predict emotion from Text Input
export const predictFromText = async (text, mode = 'match') => {
  const response = await api.post('/predict/text/', { text, mode });
  return response.data;
};
