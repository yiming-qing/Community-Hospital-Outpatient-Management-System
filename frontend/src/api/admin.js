import http, { unwrap } from './http'

// Rooms
export async function listRooms() {
  const resp = await http.get('/api/admin/rooms')
  return unwrap(resp)
}

export async function createRoom(payload) {
  const resp = await http.post('/api/admin/rooms', payload)
  return unwrap(resp)
}

export async function updateRoom(roomId, payload) {
  const resp = await http.put(`/api/admin/rooms/${roomId}`, payload)
  return unwrap(resp)
}

// Schedules
export async function listSchedules(params = {}) {
  const resp = await http.get('/api/admin/schedules', { params })
  return unwrap(resp)
}

export async function createSchedule(payload) {
  const resp = await http.post('/api/admin/schedules', payload)
  return unwrap(resp)
}

export async function updateSchedule(scheduleId, payload) {
  const resp = await http.put(`/api/admin/schedules/${scheduleId}`, payload)
  return unwrap(resp)
}

export async function deleteSchedule(scheduleId) {
  const resp = await http.delete(`/api/admin/schedules/${scheduleId}`)
  return unwrap(resp)
}

// Employees
export async function listEmployees() {
  const resp = await http.get('/api/admin/employees')
  return unwrap(resp)
}

export async function createEmployee(payload) {
  const resp = await http.post('/api/admin/employees', payload)
  return unwrap(resp)
}

export async function updateEmployee(empId, payload) {
  const resp = await http.put(`/api/admin/employees/${empId}`, payload)
  return unwrap(resp)
}

// Patients & visits search
export async function searchPatients(params = {}) {
  const resp = await http.get('/api/admin/patients/search', { params })
  return unwrap(resp)
}

export async function searchVisits(params = {}) {
  const resp = await http.get('/api/admin/visits/search', { params })
  return unwrap(resp)
}

// Statistics
export async function statsIncome(params = {}) {
  const resp = await http.get('/api/admin/statistics/income', { params })
  return unwrap(resp)
}

export async function statsVisits(params = {}) {
  const resp = await http.get('/api/admin/statistics/visits', { params })
  return unwrap(resp)
}

// Bills & income records
export async function listIncomeRecords(params = {}) {
  const resp = await http.get('/api/admin/income-records', { params })
  return unwrap(resp)
}

export async function listBills(params = {}) {
  const resp = await http.get('/api/admin/bills', { params })
  return unwrap(resp)
}

// Medical record (per-visit)
export async function getVisitMedicalRecord(visitId) {
  const resp = await http.get(`/api/admin/visits/${visitId}/medical-record`)
  return unwrap(resp)
}

export async function upsertVisitMedicalRecord(visitId, payload) {
  const resp = await http.put(`/api/admin/visits/${visitId}/medical-record`, payload)
  return unwrap(resp)
}
