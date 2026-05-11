import http from './http'

export function getAll() {

  return http.get('/api/warehouses/')
}

export function getById(id) {

  return http.get(`/api/warehouses/${id}/`)
}

export function create(data) {

  return http.post('/api/warehouses/', data)
}

export function update(id, data) {

  return http.put(
    `/api/warehouses/${id}/`,
    data
  )
}

export function remove(id) {

  return http.delete(
    `/api/warehouses/${id}/`
  )
}