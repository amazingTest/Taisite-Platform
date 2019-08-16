

import axios from 'axios'
import router from '../router'

const service = axios.create({
    baseURL: process.env.BASE_API,
    withCredentials: true,
    timeout: 60000
})

service.interceptors.response.use((response) => {
    return response.data
}, (error) => {
    if (error && error.response) {
        if (error.response.status === 401){
            router.replace({name: 'login'})
            return {'status': 'failed', 'data': '请先登录~'}
        }
        else if (error.response.status === 403){
            return {'status': 'failed', 'data': '当前用户没有操作权限哦~'}
        }
        else if (error.response.status === 500){
            return {'status': 'failed', 'data': '服务器内部错误啦~请尝试刷新重试'}
        }
        else if (error.response.status === 501){
            return {'status': 'failed', 'data': '服务器发生神秘事件~请尝试刷新重试'}
        }
        else if (error.response.status === 502){
            return {'status': 'failed', 'data': '服务器网关坏掉啦~请尝试刷新重试'}
        }
        else if (error.response.status === 503){
            return {'status': 'failed', 'data': '服务器不可用啦~请尝试刷新重试'}
        }
        else if (error.response.status === 504){
            return {'status': 'failed', 'data': '服务器响应超时啦~请尝试刷新重试'}
        }
        return Promise.reject(error.response.data)
    }
    return Promise.reject(error)
})
export default service
