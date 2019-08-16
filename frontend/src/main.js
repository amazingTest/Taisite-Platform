// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
//import routerPromise from '@/utils/getUserRouters'
import Vue from 'vue'

import ElementUI from 'element-ui'
import VueClipboard from 'vue-clipboard2'
import ToggleButton from 'vue-js-toggle-button'
import App from './App.vue'
import router from './router'
import store from './vuex/store'
import { getCookie, setCookie, delCookie} from '@/utils/cookie'
import './assets/css/element-#FF9E1B/index.css'
import './assets/css/reset.css'
import './assets/fonts/iconfont.css'
import './assets/fonts/icomoon.css'
import 'font-awesome/css/font-awesome.min.css'
import easyDialog from 'leiang-easy-dialog'
Vue.use(easyDialog)
Vue.config.productionTip = false
Vue.use(ToggleButton)
Vue.use(VueClipboard)
Vue.use(ElementUI)

router.beforeEach(async (to, from, next) => {

    if (to.matched.length === 0) { //匹配前往的路由不存在
      next('/aboutAuthor')
      return
    }

    if (['/login'].indexOf(to.path) === -1) {
      let nickName = getCookie('nickName')
      //TODO 判断太草率
      nickName !== '' ?
       to.path.trim() === '/' ?
        next('/aboutAuthor') :
       next():
      next('/login')
    }else{
      next()
    }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  components: { App },
  template: '<App/>'
})
