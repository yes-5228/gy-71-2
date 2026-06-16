import { request } from './http'

export function fetchPayments(status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : ''
  return request(`/payments${query}`)
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
