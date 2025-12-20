import http, { unwrap } from './http'

export async function listDepartments() {
  const resp = await http.get('/api/patient/departments')
  return unwrap(resp)
}

export async function createAppointment(payload) {
  const resp = await http.post('/api/patient/appointments', payload)
  return unwrap(resp)
}

export async function queryAppointments({ status } = {}) {
  const resp = await http.get('/api/patient/appointments/query', { params: { status } })
  return unwrap(resp)
}

export async function cancelAppointment(apptId) {
  const resp = await http.delete(`/api/patient/appointments/${apptId}`)
  return unwrap(resp)
}
