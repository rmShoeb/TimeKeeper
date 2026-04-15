// Production environment configuration (for Docker deployment)
export const environment = {
  production: true,
  apiUrl: '/api'  // Relative path - nginx will proxy to backend
};
