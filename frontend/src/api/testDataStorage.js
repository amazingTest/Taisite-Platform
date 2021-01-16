import request from '@/utils/request'

export function getTestDataStorageList (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testDataStorageList`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function getTestDataStorageDetail (project_id, storage_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testDataStorageList/${storage_id}`,
    headers: header,
    params: params,
    method: 'GET'
  })
}

export function addTestDataStorage (project_id, params, header) {
  return request({
    url: `/api/project/${project_id}/addTestDataStorage`,
    headers: header,
    method: 'POST',
    data: params
  })
}

export function updateTestDataStorage (project_id, storage_id, params, header) {
  return request({
    url: `/api/project/${project_id}/testDataStorageList/${storage_id}/updateStorage`,
    method: 'POST',
    headers: header,
    data: params
  })
}






