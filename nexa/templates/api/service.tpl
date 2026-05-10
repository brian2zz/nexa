import http from './http'

export function getAll() {

  return http.get('/api/{{ route_name }}/')
}

export function getById(id) {

  return http.get(`/api/{{ route_name }}/${id}/`)
}

export function create(data) {

  return http.post('/api/{{ route_name }}/', data)
}

export function update(id, data) {

  return http.put(
    `/api/{{ route_name }}/${id}/`,
    data
  )
}

export function remove(id) {

  return http.delete(
    `/api/{{ route_name }}/${id}/`
  )
}