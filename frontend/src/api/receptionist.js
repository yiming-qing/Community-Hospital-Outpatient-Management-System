import http, { unwrap } from './http'

export async function listAppointments({ status } = {}) {
  const resp = await http.get('/api/receptionist/appointments', { params: { status } })
  return unwrap(resp)
}

export async function updateAppointmentStatus(apptId, status) {
  const resp = await http.put(`/api/receptionist/appointments/${apptId}/status`, { status })
  return unwrap(resp)
}

export async function checkin(apptId, payload) {
  const resp = await http.post(`/api/receptionist/checkin/${apptId}`, payload)
  return unwrap(resp)
}

export async function onsiteRegister(payload) {
  const resp = await http.post('/api/receptionist/register', payload)
  return unwrap(resp)
}

export async function listVisits({ status } = {}) {
  const resp = await http.get('/api/receptionist/visits', { params: { status } })
  return unwrap(resp)
}

export async function updateVisitStatus(visitId, status) {
  const resp = await http.put(`/api/receptionist/visits/${visitId}/status`, { status })
  return unwrap(resp)
}

export async function payVisit(visitId, payload) {
  const resp = await http.post(`/api/receptionist/payment/${visitId}`, payload)
  return unwrap(resp)
}

export async function listPatients(params = {}) {
  const resp = await http.get('/api/receptionist/patients', { params })
  return unwrap(resp)
}

export async function listBills(params = {}) {
  const resp = await http.get('/api/receptionist/bills', { params })
  return unwrap(resp)
}

export async function listIncomeRecords(params = {}) {
  const resp = await http.get('/api/receptionist/income-records', { params })
  return unwrap(resp)
}
