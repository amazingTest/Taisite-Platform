
import request from '@/utils/request'

export function login (params, header) {
  return request({
    url: '/api/login',
    headers: header,
    method: 'POST',
    data: params
  })
}

export function logout (params, header) {
  return request({
    url: '/api/logout',
    headers: header,
    method: 'POST',
    data: params
  })
}


