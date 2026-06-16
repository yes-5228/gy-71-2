<template>
  <section class="panel">
    <SectionToolbar eyebrow="Reminders" title="到期与逾期提醒">
      <button type="button" class="ghost-button" @click="load">刷新</button>
    </SectionToolbar>

    <p v-if="error" class="error">{{ error }}</p>
    <div class="split-grid">
      <div>
        <h3>30天内到期合同</h3>
        <div class="list">
          <article v-for="contract in contracts" :key="contract.id" class="list-item">
            <strong>{{ contract.tenant_name }}</strong>
            <span>{{ contract.contract_no }} / {{ contract.workstation?.code || '-' }}</span>
            <span>到期日：{{ contract.end_date }}</span>
          </article>
          <p v-if="!contracts.length" class="empty">暂无即将到期合同</p>
        </div>
      </div>
      <div>
        <h3>逾期未收账单</h3>
        <div class="list">
          <article v-for="payment in payments" :key="payment.id" class="list-item danger-line">
            <strong>{{ payment.tenant_name }}</strong>
            <span>{{ payment.contract_no }} / {{ payment.period }}</span>
            <span>{{ currency(payment.amount) }}，应收日 {{ payment.due_date }}</span>
          </article>
          <p v-if="!payments.length" class="empty">暂无逾期账单</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchExpiringContracts, fetchOverduePayments } from '../api/reminders'
import SectionToolbar from '../components/SectionToolbar.vue'
import { currency } from '../utils/formatters'

const contracts = ref([])
const payments = ref([])
const error = ref('')

async function load() {
  error.value = ''
  try {
    const [expiring, overdue] = await Promise.all([fetchExpiringContracts(30), fetchOverduePayments()])
    contracts.value = expiring
    payments.value = overdue
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)
</script>
