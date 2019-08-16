import request from '@/utils/request'

export function getCaseList (project_id, case_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/caseList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addCase (project_id, case_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/addCase`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateCase (project_id, case_suite_id, case_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/caseList/${case_id}/updateCase`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function copyCase (project_id, case_suite_id, case_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/caseList/${case_id}/copyCase`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function exportTestCases (params, header) {
  return request({
    url: `/api/exportTestCases`,
    method: 'POST',
    headers: header,
    responseType: 'blob',
    data: params
  })

}
export function getCaseDetail (project_id, case_suite_id, case_id, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/caseList/${case_id}`,
    method: 'GET',
    headers: header,
    params: null
  })
}

export function getLastSingleTestResult (case_id, header) {
  return request({
    url: `/api/getLastSingleTestResult/${case_id}`,
    method: 'GET',
    headers: header,
    params: null
  })
}



