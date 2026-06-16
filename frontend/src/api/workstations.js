import { request } from './http'

export function fetchWorkstations(status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/workstations${query}`)
}

export function createWorkstation(payload) {
  return request('/workstations', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function updateWorkstation(id, payload) {
  return request(`/workstations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}
