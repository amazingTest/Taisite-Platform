<template>
	<el-row class="container">
		<el-col :span="24" class="header">
			<el-col :span="10" class="logo" :class="collapsed?'logo-collapse-width':'logo-width'">
				<router-link to="/" style='text-decoration: none;color: #FFFFFF;'>{{collapsed?'':sysName}}</router-link>
			</el-col>
			<el-col :span="4" class="userinfo">
				<el-dropdown trigger="hover">
					<span class="el-dropdown-link userinfo-inner"><img src="../assets/imgs/userphoto.jpg"/> {{sysUserName}}</span>
					<el-dropdown-menu slot="dropdown">
						<!--<el-dropdown-item>我的消息</el-dropdown-item>-->
						<!--<el-dropdown-item>设置</el-dropdown-item>-->
						<el-dropdown-item divided @click.native="logout">退出登录</el-dropdown-item>
					</el-dropdown-menu>
				</el-dropdown>
			</el-col>
		</el-col>
		<el-col :span="24">
			<template :index='project_id'>
				<el-menu :default-active="$route.path" class="el-menu-vertical-demo" mode="horizontal" @select="handleselect"
						 unique-opened v-show="!collapsed">
					<template v-for="item in $router.options.routes" v-if="!item.projectHidden">
						<template v-for="(items,index) in item.children">
							<el-menu-item  :class="$route.path===items.path?'is-active':''"  :index="items.path" v-if="items.leaf" :key="items.path">
								<template v-if="!items.child">
									<router-link :to="{ name: items.name, params: {id: project_id}}" style='text-decoration: none;color: #000000;'>
										<div>
											{{items.name }}
										</div>
									</router-link>
								</template>
								<template v-if="items.child">
									<router-link :to="{ name: items.children[0].name, params: {id: project_id}}" style='text-decoration: none;color: #000000;'>
										<div>
											{{items.name }}
										</div>
									</router-link>
								</template>
							</el-menu-item>
							<el-submenu :index="index+''" v-if="!items.leaf">
								<template slot="title">{{items.name}}</template>
								<el-menu-item v-for="child in items.children" :key="child.path" :index="child.path">
									{{child.name}}
								</el-menu-item>
							</el-submenu>
						</template>
					</template>
				</el-menu>
			</template>
			<strong class="title" style="margin-bottom: 20px">{{$route.name}}</strong>
		</el-col>
		<el-col :span="24">
			<transition name="fade" mode="out-in">
				<router-view></router-view>
			</transition>
		</el-col>
	</el-row>
</template>

<script>
    import {getCookie, delCookie} from '@/utils/cookie'
    import {logout} from '@/api/user'
    export default {
        data() {
            return {
                tabPosition: 'top',
                project_id:'',
                sysName:'泰斯特平台',
                collapsed:false,
                sysUserName: '未知用户',
                sysUserAvatar: '',
            }
        },
        methods: {
            handleselect: function (a, b) {
            },
            onSubmit() {
                //console.log('submit!');
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
                logout(params, header).then((res) => {
                    let self = this
                    if (res.status === 'ok') {
                      self.$message.success({
                        message: res.data,
                        center: true,
                      })
                      self.$router.push({name: 'login'})
                    }else{
                      self.$message.error({
                        message: res.data,
                        center: true,
                      })
                    }
                  });
              }).catch((error) => {
                  let self = this
                  self.$message.error({
                    message: '退出登录失败!',
                    center: true,
                  })
                });
            },
            showMenu(i,status){
                this.$refs.menuCollapsed.getElementsByClassName('submenu-hook-'+i)[0].style.display=status?'block':'none';
            },
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
			color:#fff;
			.userinfo {
				text-align: right;
				padding-right: 35px;
				float: right;
				.userinfo-inner {
					cursor: pointer;
					color:#fff;
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
				height:60px;
				font-size: 22px;
				padding-left:20px;
				padding-right:20px;
				border-color: rgba(238,241,146,0.3);
				border-right-width: 1px;
				border-right-style: solid;
				img {
					width: 40px;
					float: left;
					margin: 10px 10px 10px 18px;
				}
				.txt {
					color:#fff;
				}
			}
			.logo-width{
				width:230px;
			}
			.logo-collapse-width{
				width:60px
			}
			.tools{
				padding: 0px 23px;
				width:14px;
				height: 60px;
				line-height: 60px;
				cursor: pointer;
			}
		}
		.title {
			width: 200px;
			float: left;
			color: #475669;
			font-size: 25px;
			margin: 15px;
			margin-left: 35px;
			margin-bottom: 0px;
			font-family: Arial;
		}
	}
</style>
