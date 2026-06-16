import { request } from './http'

export function fetchExpiringContracts(days = 30) {
  return request(`/reminders/expiring-contracts?days=${days}`)
}

export function fetchOverduePayments() {
  return request('/reminders/overdue-payments')
}
