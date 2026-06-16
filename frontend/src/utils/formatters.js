export function currency(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

export function statusText(value) {
  const map = {
    available: '可租',
    leased: '已租',
    maintenance: '维护',
    reserved: '预留',
    active: '履行中',
    terminated: '已终止',
    expired: '已到期',
    unpaid: '待收',
    paid: '已收',
    overdue: '逾期'
  }
  return map[value] || value
}

export function todayISO() {
  return new Date().toISOString().slice(0, 10)
}
