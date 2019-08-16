import request from '@/utils/request'

export function startInterfaceTest (params, header) {
  return request({
    url: `/api/startInterfaceTesting`,
    method: 'POST',
    headers: header,
    data: params
  })
}
