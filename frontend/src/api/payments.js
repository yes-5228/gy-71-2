import { request } from './http'

function buildFilterQuery(filters = {}) {
  const params = new URLSearchParams()
  if (filters.floor) params.set('floor', filters.floor)
  if (filters.tenant) params.set('tenant', filters.tenant)
  if (filters.period) params.set('period', filters.period)
  if (filters.status) params.set('status', filters.status)
  if (filters.expense_type) params.set('expense_type', filters.expense_type)
  const qs = params.toString()
  return qs ? `?${qs}` : ''
}

export function fetchPayments(filters = {}) {
  return request(`/payments${buildFilterQuery(filters)}`)
}

export function fetchPaymentSummary(filters = {}) {
  return request(`/payments/summary${buildFilterQuery(filters)}`)
}

export function fetchFilterOptions() {
  return request('/payments/filter-options')
}

export function exportPaymentsCsv(filters = {}) {
  const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'
  return `${base}/payments/export${buildFilterQuery(filters)}`
}

export function createPayment(payload) {
  return request('/payments', {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export function markPaymentPaid(id, payload) {
  return request(`/payments/${id}/mark-paid`, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}
