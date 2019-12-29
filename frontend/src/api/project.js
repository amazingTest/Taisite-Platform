import request from '@/utils/request'

export function getProjects (params, header) {
  return request({
    url: `/api/project/projectList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getProjectInfo(project_id) {
  return request({
    url: `/api/project/${project_id}`,
    method: 'GET'
  })
}

export function addProject (params, header) {
  return request({
    url: `/api/project/addProject`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateProject (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/updateProject`,
    method: 'POST',
    headers: header,
    data: params
  })
}

