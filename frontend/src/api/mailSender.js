import request from '@/utils/request'

export function getMailSender (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/mailSenderList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addMailSender(project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addMailSender`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateMailSender (project_id, sender_id, params, header) {
  return request({
    url: `/api/project/${project_id}/mailSenderList/${sender_id}/updateMailSender`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function testMailSender (params, header) {
  return request({
    url: `/api/testEmailSender`,
    method: 'POST',
    headers: header,
    data: params
  })
}


