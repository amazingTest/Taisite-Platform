import Vue from 'vue'
import Router from 'vue-router'
import interfaceProjectList from '@/views/interfaceTestProject/ProjectList'
import login from '@/views/Login'
import projectInfo from '@/views/Project'
import home from '@/views/Home'
import about from '@/views/About'
import automationTest from '@/views/interfaceTestProject/api/automation/AutomationTest'
import cronList from '@/views/interfaceTestProject/api/automation/CronList'
import caseSuiteList from '@/views/interfaceTestProject/api/automation/CaseSuiteList'
import caseApiList from '@/views/interfaceTestProject/api/automation/CaseApiList'
import addCaseApi from '@/views/interfaceTestProject/api/automation/AddCaseApi'
import updateCaseApi from '@/views/interfaceTestProject/api/automation/UpdateCaseApi'
import globalHost from '@/views/interfaceTestProject/global/Globalhost'
import globalMail from '@/views/interfaceTestProject/global/GlobalMail'
import projectReport from '@/views/interfaceTestProject/ProjectReport'
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/login',
      name: 'login',
      component: login,
      hidden: true,
      projectHidden: true
    },
    {
      path: '/',
      component: home,
      name: '',
      projectHidden: true,
      children: [
        { path: '/interfaceProjectList', component: interfaceProjectList, iconCls:'fa fa-plug', name: '接口测试'},
        { path: '/aboutAuthor', component: about, iconCls:'fa fa-id-card-o', name: '关于作者'},
      ]
    },
    {
      path: '/interfaceTestProject/:project_id',
      component: projectInfo,
      name: '项目',
      hidden: true,
      children: [
      {
        path: '/automationTest/:project_id',
        component: automationTest,
        name: '自动化测试',
        leaf: true,
        child: true,
        children: [
          {   path: '/interfaceTestProject/:project_id/caseSuiteList', component: caseSuiteList, name: '用例列表'},
          {   path: '/interfaceTestProject/:project_id/caseApiList/caseSuiteId=:case_suite_id', component: caseApiList, name: '用例接口列表'},
          {   path: '/interfaceTestProject/:project_id/updateCaseApi/caseSuiteId=:case_suite_id/testingCaseId=:case_id', component: updateCaseApi, name: '修改用例'}
        ]
      },
        {
            path: '/interfaceTestProject/:project_id/GlobalHost',
            component: globalHost,
            name: 'Host配置',
            leaf: true
        },
        {
            path: '/interfaceTestProject/:project_id/GlobalMail',
            component: globalMail,
            name: '邮箱配置',
            leaf: true
        },
        {
          path: '/interfaceTestProject/:project_id/CronList',
          component: cronList,
          name: '定时任务',
          leaf: true
        },
        {   path: '/interfaceTestProject/:project_id/projectReport', component: projectReport, name: '测试报告', leaf: true}
      ]
    }
  ]
})
