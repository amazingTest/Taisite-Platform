import request from '@/utils/request'

export function getHosts (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/hostList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addHost(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addHost`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateHost (project_id, host_id, params, header) {
  return request({
    url: `/api/project/${project_id}/hostList/${host_id}/updateHost`,
    method: 'POST',
    headers: header,
    data: params
  })
}

