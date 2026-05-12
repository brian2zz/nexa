import axios from 'axios';

export default {
  list() {
    return axios.get('/api/{{ route_name }}/');
  },
  get(id) {
    return axios.get(`/api/{{ route_name }}/${id}/`);
  },
  create(data) {
    return axios.post('/api/{{ route_name }}/', data);
  },
  update(id, data) {
    return axios.put(`/api/{{ route_name }}/${id}/`, data);
  },
  delete(id) {
    return axios.delete(`/api/{{ route_name }}/${id}/`);
  }
};