import http from './http'

export function getAll() {

  return http.get('/api/categories/')
}

export function getById(id) {

  return http.get(`/api/categories/${id}/`)
}

export function create(data) {

  return http.post('/api/categories/', data)
}

export function update(id, data) {

  return http.put(
    `/api/categories/${id}/`,
    data
  )
}

export function remove(id) {

  return http.delete(
    `/api/categories/${id}/`
  )
}