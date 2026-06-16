import { request } from './http'

export function fetchDashboardStats() {
  return request('/dashboard/stats')
}
