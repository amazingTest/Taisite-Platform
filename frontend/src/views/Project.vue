<template>
  <el-row class="container">
    <header-view :projectName="projectName"></header-view>
    <el-col :span="24">
      <template :index='project_id'>
        <el-menu :default-active="$route.path" class="el-menu-vertical-demo" mode="horizontal" @select="handleselect"
                 unique-opened v-show="!collapsed">
          <template v-for="item in $router.options.routes" v-if="!item.projectHidden">
            <template v-for="(items,index) in item.children">
              <el-menu-item :class="$route.path===items.path?'is-active':''" :index="items.path" v-if="items.leaf"
                            :key="items.path">
                <template v-if="!items.child">
                  <router-link :to="{ name: items.name, params: {id: project_id}}"
                               style='text-decoration: none;color: #000000;'>
                    <div>
                      {{items.name }}
                    </div>
                  </router-link>
                </template>
                <template v-if="items.child">
                  <router-link :to="{ name: items.children[0].name, params: {id: project_id}}"
                               style='text-decoration: none;color: #000000;'>
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
    import Header from "./common/Header";
    import {getProjectInfo} from "../api/project";

    export default {
        components: {Header},
        data() {
            return {
                project_id: '',
                projectName: '',
                collapsed: false
            }
        },
        methods: {
            handleselect: function (a, b) {
            },
            onSubmit() {
                //console.log('submit!');
            },
            showMenu(i, status) {
                this.$refs.menuCollapsed.getElementsByClassName('submenu-hook-' + i)[0].style.display = status ? 'block' : 'none';
            },
        },
        mounted() {
            getProjectInfo(this.$route.params.project_id).then((res) => {
                if (res.status === 'ok') {
                    this.projectName = res.data.name;
                }
            })
        }
    }

</script>

<style scoped lang="scss">

  .container {
    position: absolute;
    top: 0px;
    bottom: 0px;
    width: 100%;

    .title {
      width: 200px;
      float: left;
      color: #475669;
      font-size: 25px;
      margin: 15px 15px 0px 35px;
      font-family: Arial;
    }
  }
</style>
