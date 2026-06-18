<template>
  <section class="panel">
    <SectionToolbar eyebrow="Payments" title="费用收缴">
      <div class="toolbar-actions">
        <a v-if="csvUrl" :href="csvUrl" download="payments.csv" class="ghost-button">导出 CSV</a>
      </div>
    </SectionToolbar>

    <div class="filter-bar">
      <select v-model="filters.floor" @change="loadData">
        <option value="">全部楼层</option>
        <option v-for="f in options.floors" :key="f" :value="f">{{ f }}</option>
      </select>
      <select v-model="filters.tenant" @change="loadData">
        <option value="">全部租户</option>
        <option v-for="t in options.tenants" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="filters.period" @change="loadData">
        <option value="">全部账期</option>
        <option v-for="p in options.periods" :key="p" :value="p">{{ p }}</option>
      </select>
      <select v-model="filters.status" @change="loadData">
        <option value="">全部状态</option>
        <option value="unpaid">待收</option>
        <option value="overdue">逾期</option>
        <option value="paid">已收</option>
      </select>
      <select v-model="filters.expense_type" @change="loadData">
        <option value="">全部费用类型</option>
        <option v-for="e in options.expense_types" :key="e" :value="e">{{ expenseTypeText(e) }}</option>
      </select>
    </div>

    <div v-if="summary" class="summary-grid">
      <div class="summary-card">
        <span>账单总额</span>
        <strong>{{ currency(summary.total_amount) }}</strong>
      </div>
      <div class="summary-card ok">
        <span>已收金额</span>
        <strong>{{ currency(summary.paid_amount) }}</strong>
      </div>
      <div class="summary-card warn">
        <span>待收金额</span>
        <strong>{{ currency(summary.unpaid_amount) }}</strong>
      </div>
      <div class="summary-card danger">
        <span>逾期金额</span>
        <strong>{{ currency(summary.overdue_amount) }}</strong>
        <small v-if="summary.overdue_count">{{ summary.overdue_count }} 笔逾期</small>
      </div>
    </div>

    <div v-if="summary && summary.overdue_alert_count > 0" class="overdue-alert">
      <strong>逾期提醒</strong>
      <span>当前筛选下有 {{ summary.overdue_alert_count }} 笔逾期账单，合计 {{ currency(summary.overdue_alert_amount) }}，请及时催收。</span>
    </div>

    <form class="form-grid" @submit.prevent="submit">
      <select v-model.number="form.contract_id" required>
        <option value="" disabled>选择合同</option>
        <option v-for="contract in activeContracts" :key="contract.id" :value="contract.id">
          {{ contract.contract_no }} / {{ contract.tenant_name }}
        </option>
      </select>
      <input v-model="form.period" placeholder="账期 2026-06" required />
      <input v-model.number="form.amount" type="number" min="0" placeholder="应收金额" required />
      <input v-model="form.due_date" type="date" required />
      <select v-model="form.expense_type" required>
        <option value="rent">租金</option>
        <option value="deposit">押金</option>
        <option value="management_fee">物业费</option>
        <option value="utility">水电费</option>
        <option value="other">其他</option>
      </select>
      <input v-model="form.note" placeholder="备注" />
      <button type="submit">创建账单</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>合同</th>
            <th>租户</th>
            <th>楼层</th>
            <th>账期</th>
            <th>费用类型</th>
            <th>金额</th>
            <th>到期日</th>
            <th>状态</th>
            <th>收款</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="payment in payments" :key="payment.id">
            <td>{{ payment.contract_no }}</td>
            <td>{{ payment.tenant_name }}</td>
            <td>{{ payment.floor || '-' }}</td>
            <td>{{ payment.period }}</td>
            <td>{{ expenseTypeText(payment.expense_type) }}</td>
            <td>{{ currency(payment.amount) }}</td>
            <td>{{ payment.due_date }}</td>
            <td><StatusBadge :value="payment.status" /></td>
            <td>
              <button v-if="payment.status !== 'paid'" type="button" class="small-button" @click="pay(payment.id)">
                确认收款
              </button>
              <span v-else>{{ payment.method || '已入账' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { fetchContracts } from '../api/contracts'
import { createPayment, exportPaymentsCsv, fetchFilterOptions, fetchPayments, fetchPaymentSummary, markPaymentPaid } from '../api/payments'
import SectionToolbar from '../components/SectionToolbar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { currency, expenseTypeText, todayISO } from '../utils/formatters'

const payments = ref([])
const activeContracts = ref([])
const summary = ref(null)
const options = ref({ floors: [], tenants: [], periods: [], expense_types: [] })
const error = ref('')

const filters = reactive({
  floor: '',
  tenant: '',
  period: '',
  status: '',
  expense_type: ''
})

const csvUrl = computed(() => exportPaymentsCsv(filters))

const form = reactive({
  contract_id: '',
  period: todayISO().slice(0, 7),
  amount: 0,
  due_date: todayISO(),
  expense_type: 'rent',
  note: ''
})

watch(
  () => form.contract_id,
  (id) => {
    const contract = activeContracts.value.find((item) => item.id === Number(id))
    if (contract) {
      form.amount = Number(contract.monthly_rent)
    }
  }
)

async function loadFilterOptions() {
  try {
    options.value = await fetchFilterOptions()
  } catch (err) {
    error.value = err.message
  }
}

async function loadPayments() {
  error.value = ''
  try {
    payments.value = await fetchPayments(filters)
  } catch (err) {
    error.value = err.message
  }
}

async function loadSummary() {
  try {
    summary.value = await fetchPaymentSummary(filters)
  } catch (err) {
    error.value = err.message
  }
}

async function loadData() {
  await Promise.all([loadPayments(), loadSummary()])
}

async function loadContracts() {
  activeContracts.value = await fetchContracts('active')
}

async function load() {
  try {
    await Promise.all([loadFilterOptions(), loadData(), loadContracts()])
  } catch (err) {
    error.value = err.message
  }
}

async function submit() {
  error.value = ''
  try {
    await createPayment({ ...form, contract_id: Number(form.contract_id) })
    Object.assign(form, { contract_id: '', period: todayISO().slice(0, 7), amount: 0, due_date: todayISO(), expense_type: 'rent', note: '' })
    await Promise.all([loadPayments(), loadSummary(), loadFilterOptions()])
  } catch (err) {
    error.value = err.message
  }
}

async function pay(id) {
  error.value = ''
  try {
    await markPaymentPaid(id, { method: 'bank_transfer', note: '前台确认收款' })
    await Promise.all([loadPayments(), loadSummary()])
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)
</script>
