import axios from 'axios';

// Konfigurasi Standar Integrasi CSRF Django Backend
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

export default {
  list() {
    return axios.get('/api/v1/{{ app_name }}/{{ route_name }}/');
  },
  get(id) {
    return axios.get(`/api/v1/{{ app_name }}/{{ route_name }}/${id}/`);
  },
  create(data) {
    return axios.post('/api/v1/{{ app_name }}/{{ route_name }}/', data);
  },
  update(id, data) {
    return axios.put(`/api/v1/{{ app_name }}/{{ route_name }}/${id}/`, data);
  },
  delete(id) {
    return axios.delete(`/api/v1/{{ app_name }}/{{ route_name }}/${id}/`);
  }
};