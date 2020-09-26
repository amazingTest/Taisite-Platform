import request from '@/utils/request'

export function getReportList (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/reportsList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getReportDetail (project_id, report_id, header) {
  return request({
    url: `/api/project/${project_id}/reportsList/${report_id}`,
    headers: header,
    params: null,
    method: 'GET'
  })
}

export function exportReportDetail (project_id, report_id, header) {
  return request({
    url: `/api/project/${project_id}/reportsList/${report_id}/export`,
    headers: header,
    responseType: 'blob',
    method: 'POST',
    data: null
  })
}

