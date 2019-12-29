<template>
  <el-col :span="24" class="header">
    <el-col :span="8" class="logo" :class="collapsed?'logo-collapse-width':'logo-width'">
      <router-link to="/" style='text-decoration: none;color: #FFFFFF;'>
        <img id="logo" src="../../assets/imgs/logo.jpg"/>
        {{collapsed?'':sysName}}
      </router-link>
    </el-col>
    <el-col :span="1">
      <div class="tools" @click.prevent="collapse">
        <i class="fa fa-align-justify"></i>
      </div>
    </el-col>
    <el-col :span="11" class="project-info" v-if="projectName">
      <span class="project-info-inner">{{projectName}}</span>
    </el-col>
    <el-col :span="4" class="userinfo">
      <el-dropdown trigger="hover">
					<span class="el-dropdown-link userinfo-inner">
						{{sysUserName}}
						<img id="userphoto" src="../../assets/imgs/userphoto.jpg"/>
					</span>
        <el-dropdown-menu slot="dropdown">
          <!--<el-dropdown-item>我的消息</el-dropdown-item>-->
          <!--<el-dropdown-item>设置</el-dropdown-item>-->
          <el-dropdown-item divided>
            <a target="_blank" href="https://shimo.im/docs/8TqxG3Ttjvj9yT8T">
              使用教程
            </a>
          </el-dropdown-item>
          <el-dropdown-item ref="logoutBtn" divided @click.native="logout">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </el-col>
  </el-col>
</template>

<script>
    import {getCookie, delCookie} from "../../utils/cookie";
    import {logout} from "../../api/user";

    export default {
        name: "Header",
        props: ['projectName'],
        data() {
            return {
                sysName: '泰斯特平台',
                collapsed: false,
                sysUserName: '未知用户',
                // sysUserAvatar: '',

            }
        },
        methods: {
            onSubmit() {
                //console.log('submit!');
            },
            handleselect: function (a, b) {
            },
            //退出登录
            logout: function () {
                let _this = this;
                this.$confirm('确认退出吗?', '提示', {
                    //type: 'warning'
                }).then(() => {
                    delCookie('nickName')
                    let params = {}
                    let header = {}
                    this.$refs.logoutBtn.loading = true
                    logout(params, header).then((res) => {
                        let self = this
                        this.$refs.logoutBtn.loading = false
                        if (res.status === 'ok') {
                            self.$message.success({
                                message: res.data,
                                center: true,
                            })
                            self.$router.push({name: 'login'})
                        } else {
                            self.$message.error({
                                message: res.data,
                                center: true,
                            })
                        }
                    });
                }).catch((error) => {
                    self.$message.error({
                        message: '退出登录失败!',
                        center: true,
                    })
                });
            },
            //折叠导航栏
            collapse: function () {
                this.collapsed = !this.collapsed;
                this.$emit('collapse', this.collapsed);
            },
            showMenu(i, status) {
                this.$refs.menuCollapsed.getElementsByClassName('submenu-hook-' + i)[0].style.display = status ? 'block' : 'none';
            }
        },
        mounted() {
            let nickName = unescape(getCookie('nickName').replace(/\\u/g, '%u'));
            this.sysUserName = nickName || '未知用户';
        }
    }
</script>


<style scoped lang="scss">
  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;

    .header {
      height: 60px;
      line-height: 60px;
      background: #FF9E1B;
      color: #fff;

      .userinfo {
        text-align: right;
        padding-right: 35px;
        float: right;

        .userinfo-inner {
          cursor: pointer;
          color: #fff;

          img {
            width: 40px;
            height: 40px;
            border-radius: 20px;
            margin: 10px 0px 10px 10px;
            float: right;
          }
        }
      }

      .logo {
        //width:230px;
        height: 60px;
        font-size: 22px;
        padding-left: 10px;
        padding-right: 10px;
        border-color: rgba(238, 241, 146, 0.3);
        border-right-width: 1px;
        border-right-style: solid;

        img {
          width: 40px;
          float: left;
          margin: 10px 15px 10px 0px;
        }

        .txt {
          color: #fff;
        }
      }

      .logo-width {
        width: 230px;
      }

      .logo-collapse-width {
        width: 60px
      }

      .tools {
        padding: 0px 23px;
        width: 14px;
        height: 60px;
        line-height: 60px;
        cursor: pointer;
      }

      .project-info {
        text-align: left;
        padding-right: 35px;
        float: left;
        font-size: 22px;
        line-height: 60px;

        .project-info-inner {
          cursor: pointer;
          color: #fff;
        }
      }
    }
  }
</style>
