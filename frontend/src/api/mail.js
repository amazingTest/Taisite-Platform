import request from '@/utils/request'

export function getMails (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/mailList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addMail(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addMail`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateMail (project_id, mail_id, params, header) {
  return request({
    url: `/api/project/${project_id}/mailList/${mail_id}/updateMail`,
    method: 'POST',
    headers: header,
    data: params
  })
}

