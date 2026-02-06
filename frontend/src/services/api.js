import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

export const vagasService = {
  listar: (filtros = {}) => api.get('/vagas/', { params: filtros }),
  obter: (id) => api.get(`/vagas/${id}`),
  criar: (data) => api.post('/vagas/', data),
  atualizar: (id, data) => api.patch(`/vagas/${id}`, data),
  atualizarStatus: (id, status) => api.patch(`/vagas/${id}/status`, null, { params: { status } }),
  deletar: (id) => api.delete(`/vagas/${id}`),
};

export const statsService = {
  obter: () => api.get('/stats/'),
};

export const scraperService = {
  coletarTudo: () => api.post('/scraper/all'),
  coletarIndeed: () => api.post('/scraper/indeed'),
  coletarLinkedin: () => api.post('/scraper/linkedin'),
  coletarPosts: () => api.post('/scraper/posts'),
};

export default api;
