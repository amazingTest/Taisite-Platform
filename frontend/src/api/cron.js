import request from '@/utils/request'

export function getCrons (params, header) {
  return request({
    url: `/api/cronList`,
    method: 'GET',
    headers: header,
    params: params
  })
}

export function addCron (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addCron`,
    method: 'POST',
    headers: header,
    data: params
  })
}

 export function updateCron (cron_id, params, header) {
   return request({
     url: `/api/cronList/${cron_id}/updateCron`,
     method: 'POST',
     headers: header,
     data: params
   })
 }

export function pauseCron (cron_id, params, header) {
  return request({
    url: `/api/cronList/${cron_id}/pauseCron`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function resumeCron (cron_id, params, header) {
  return request({
    url: `/api/cronList/${cron_id}/resumeCron`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function delCron (cron_id, params, header) {
  return request({
    url: `/api/cronList/${cron_id}/delCron`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function startScheduler(params, header) {
  return request({
    url: `/api/cronList/start`,
    method: 'POST',
    headers: header,
    data: params
  })
}

export function shutdownScheduler (params, header) {
  return request({
    url: `/api/cronList/shutdown`,
    method: 'POST',
    headers: header,
    data: params
  })
}







