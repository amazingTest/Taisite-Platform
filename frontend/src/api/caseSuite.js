import request from '@/utils/request'

export function getCaseSuiteList (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addCaseSuite (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addCaseSuite`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateCaseSuite (project_id, case_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/updateCaseSuite`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function copyCaseSuite (project_id, case_suite_id, params, header) {
  return request({
    url: `/api/project/${project_id}/caseSuiteList/${case_suite_id}/copyCaseSuite`,
    method: 'POST',
    headers: header,
    data: params
  })
}

