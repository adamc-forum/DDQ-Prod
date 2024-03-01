import axios from 'axios';

const API = axios.create({
  // Development
  baseURL: 'http://127.0.0.1:8000/'

  // Prod
  // baseURL: 'https://ddq-web-app.azurewebsites.net/'
});

export default API;
