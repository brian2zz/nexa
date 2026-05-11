import http from './http'

export function getAll() {

  return http.get('/api/products/')
}

export function getById(id) {

  return http.get(`/api/products/${id}/`)
}

export function create(data) {

  return http.post('/api/products/', data)
}

export function update(id, data) {

  return http.put(
    `/api/products/${id}/`,
    data
  )
}

export function remove(id) {

  return http.delete(
    `/api/products/${id}/`
  )
}