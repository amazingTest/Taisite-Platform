<template>
  <div class="aitest-login">
    <div class="aitest-login-main">
      <div style="text-align:center;margin-bottom:20px;">
        <img
          src="../assets/imgs/logo.jpg"
          style="margin-bottom: 8px"
          width="100px"
          height="90px">
        <div style="font-size: 24px;color: #e6a721">泰斯特平台</div>
      </div>
      <form
        method="post"
        class="login-form">
        <div style="margin-bottom:10px;">
          <!--<i style="background: url('/img/账号.png') no-repeat" class="login-icon"></i>-->
          <input
            id="login-username"
            type="text"
            class="login-input"
            placeholder="请输入帐号"
            v-model="username"
            required
            autofocus
            @keyup.enter="submit">
        </div>
        <!--<i style="background: url('/img/密码.png') no-repeat" class="login-icon"></i>-->
        <input
          id="login-password"
          type="password"
          class="login-input"
          placeholder="请输入密码"
          v-model="password"
          @keyup.enter="submit">
        <div style="margin-bottom: 50px;color: red;text-align: center;"/>
        <el-button
          id="login-checkout"
          class="login-btn"
          ref = 'loginBtn'
          type="primary"
          @click="submit">登录</el-button>
      </form>
    </div>
  </div>
</template>

<script>
import { login } from '@/api/user'
import { getCookie, setCookie, delCookie} from '@/utils/cookie'
export default {
    data () {
        return {
            username: '',
            password: ''
        }
    },
    methods: {
        async submit () {
            let self = this
            let header = {};
            let params = {username: self.username, password: self.password}
            this.$refs.loginBtn.loading = true;
            const res = await login(params, header).then((res) => {
              this.$refs.loginBtn.loading = false;
              if (res.status === 'ok') {
                let nickName = res.data.nickName
                setCookie('nickName', nickName, 365)
                this.$router.push('/')
              }else{
                self.$message.error({
                  message: res.data,
                  center: true,
                })
              }
            });
        }
    }
}
</script>

<style scoped>
  .aitest-login{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    background: url(../assets/imgs/Banner.jpg);
    background-size: 100% 100%;
    -moz-background-size:100% 100%;
    -webkit-background-size:100% 100%;
    background-repeat: no-repeat;
  }
  .aitest-login-main{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 500px;
    padding: 20px;
    border-radius: 2px;
    background-color: #fff;
  }
  .login-btn{
    width: 440px;
  }
  @media screen and (max-width:500px) {
    .aitest-login{
      background: #fff;
    }
    .aitest-login-main{
      width: 90%;
      box-sizing: border-box;
      border: none;
      box-shadow: none;
      background-color: transparent;
    }
    .login-btn{
      width: 100%;
    }
  }
  .login-form{
    text-align: center;
    position: relative;
  }
  .login-input{
    background: transparent;
    width: 300px;
    height: 40px;
    margin-bottom: 10px;
    border: 0;
    outline: 0;
    border-bottom: thin solid #ccc;
    box-shadow: 0 0 0px 1000px transparent inset;
  }
  .login-icon{
    margin-right: 10px;
    display: inline-block;
    width: 20px;
    height: 20px;
  }
</style>
