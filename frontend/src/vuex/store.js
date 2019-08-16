import Vue from 'vue'
import Vuex from 'vuex'
import * as actions from './actions'
import * as getters from './getters'

Vue.use(Vuex);

// 应用初始状态
const state = {
    initPageInfo:{
      size: 10,
      skip: 0,
      sortBy: 'createAt',
      order: 'descending',
      currentPage: 1,
    },
    apiCasePageInfo:[],
    apiCaseSuitePageInfo:[],
};

// 定义所需的 mutations
const mutations = {
    setApiCasePageInfo(state, info) {
        let identicalIdIndex = state.apiCasePageInfo.findIndex(i => i.caseSuiteId === info.caseSuiteId)
        let hasIdenticalInfo = identicalIdIndex === -1 ? false : true
        hasIdenticalInfo ? state.apiCasePageInfo[identicalIdIndex] =
         Object.assign({}, state.apiCasePageInfo[identicalIdIndex], info):
          state.apiCasePageInfo.push(Object.assign({}, state.initPageInfo, info))
    },
    setApiCaseSuitePageInfo(state, info) {
        let identicalIdIndex = state.apiCaseSuitePageInfo.findIndex(i => i.projectId === info.projectId)
        let hasIdenticalInfo = identicalIdIndex === -1 ? false : true
        hasIdenticalInfo ? state.apiCaseSuitePageInfo[identicalIdIndex] =
         Object.assign({}, state.apiCaseSuitePageInfo[identicalIdIndex], info):
          state.apiCaseSuitePageInfo.push(Object.assign({}, state.initPageInfo, info))
    }
};

// 创建 store 实例
export default new Vuex.Store({
    actions,
    getters,
    state,
    mutations,
    namespaces: true
})
