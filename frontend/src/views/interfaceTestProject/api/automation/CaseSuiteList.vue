<template>
    <section>
        <!--工具条-->
        <el-col class="toolbar" :span="24">
            <el-form :inline="true" :model="filters" @submit.native.prevent>
                <router-link :to="{ name: '接口测试'}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="return-list"><i class="el-icon-d-arrow-left"return-list style="margin-right: 5px"></i> 回首页</el-button>
                </router-link>
                <el-form-item style="margin-left: 35px">
                    <el-button type="primary" class="el-icon-plus" @click="handleAdd"> 新增用例</el-button>
                </el-form-item>

                <el-form-item style="margin-left: 5px">
                  <el-button type="primary" class="el-icon-caret-right" :disabled="!hasSels" @click="executeTest"> 执行测试</el-button>
                </el-form-item>
                <el-select v-model="testUrl" @visible-change="checkActiveEnv" clearable placeholder="测试环境" style="margin-left: 5px">
                  <el-option v-for="(item,index) in Host" :key="index+''" :label="item.name" :value="item.host"></el-option>
                </el-select>

                <el-form-item style="margin-left: 5px">
                  <el-tooltip class="item" effect="dark" content="只接收 xls / xlsx 哦~" placement="top-start">
                    <el-upload
                     :action="getImportUrl"
                     :before-upload="onBeforeUpload"
                     :on-success="onSuccessUpload"
                     :on-error="onErrorUpload"
                     :on-progress="onProgressUpload"
                     :show-file-list="false"
                     :with-credentials='true'
                     :data="importExtraData"
                     >
                      <el-button class="el-icon-upload2" :disabled="importLoading" type="primary" style="margin-left: 5px"> 用例导入</el-button>
                    </el-upload>
                   </el-tooltip>
                </el-form-item>
                <el-form-item style="margin-left: 5px">
                  <el-tooltip class="item" effect="dark" content="导出格式是 xlsx 哦~" placement="top-start">
                    <el-button class="el-icon-download" :loading="exportLoading" :disabled="!hasSels" type="primary" style="margin-right: 3px" @click="exportCases"> 用例导出</el-button>
                  </el-tooltip>
                </el-form-item>

                <div style="float: right; margin-right: 132px">
                  <el-form-item>
                    <el-input v-model.trim="filters.name" placeholder="用例名称" @keyup.enter.native="getCaseSuites"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" class="el-icon-search" @click="getCaseSuites"> 查询</el-button>
                  </el-form-item>
                </div>
            </el-form>
        </el-col>

        <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false" style="width: 65%; left: 17.5%">
            <el-form :model="editForm"  :rules="editFormRules" ref="editForm" label-width="80px">
                <el-form-item label="名称" prop="name">
                    <el-input v-model.trim="editForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="4" v-model.trim="editForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--新增界面-->
        <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width: 65%; left: 17.5%">
            <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model.trim="addForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="4" v-model.trim="addForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="addFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--列表-->
        <el-table @sort-change='sortChange' :data="Case" :row-style="reportRowStyle" :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
            <el-table-column type="selection" min-width="5%">
            </el-table-column>
            <el-table-column sortable='custom' prop="name" label="用例名称" min-width="60%" show-overflow-tooltip>
                <template slot-scope="scope">
                    <el-icon name="name"></el-icon>
                    <router-link :to="{ name: '用例接口列表', params: {
                        case_suite_id: scope.row._id,
                        showWarmPrompt:true}}" style='text-decoration: none;'>
                            {{ scope.row.name }}
                    </router-link>
                </template>
            </el-table-column>
            <el-table-column sortable='custom' prop="description" label="描述" min-width="30%" show-overflow-tooltip>
            </el-table-column>
            <el-table-column sortable='custom' prop="createAt" label="创建时间" min-width="30%" show-overflow-tooltip>
            </el-table-column>
            <el-table-column sortable='custom' prop="creatorNickName" label="创建者" min-width="15%" show-overflow-tooltip>
            </el-table-column>
            <el-table-column sortable='custom' prop="lastUpdateTime" label="最后更新时间" min-width="30%" show-overflow-tooltip>
            </el-table-column>
            <el-table-column sortable='custom' prop="lastUpdatorNickName" label="最后更新人" min-width="20%" show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="15%" sortable='custom'>
                <template slot-scope="scope">
                    <img v-show="scope.row.status" src="../../../../assets/imgs/icon-yes.svg"/>
                    <img v-show="!scope.row.status" src="../../../../assets/imgs/icon-no.svg"/>
                </template>
            </el-table-column>
            <el-table-column label="操作" min-width="80%">
                <template slot-scope="scope">
                    <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
                    <el-button class="copyBtn" size="small" :loading="copyLoading" @click="copyCaseSuite(scope.$index, scope.row)">复制</el-button>
                    <el-button
                      type="info"
                      size="small"
                      :loading="statusChangeLoading"
                      @click="handleChangeStatus(scope.$index, scope.row)">
                        {{scope.row.status===false?'启用':'禁用'}}
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>

      <!--工具条-->
      <el-col :span="24" class="toolbar">
        <!--<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>-->
        <el-pagination
          style="float: right"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page.sync="currentPage"
          v-if="totalNum != 0"
          :page-sizes="[10, 20, 40]"
          :page-size="size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalNum">
        </el-pagination>
      </el-col>
      <a
        class="js-download-doc"
        :href="downloadLink"
        :download="downloadName"
        v-show="false"
      />
    </section>
</template>

<script>
    import {getCaseSuiteList, addCaseSuite, updateCaseSuite, copyCaseSuite} from '../../../../api/caseSuite';
    import {exportTestCases} from '../../../../api/testCase';
    import {getHosts} from "../../../../api/host";
    import {getCrons, addCron, pauseCron, resumeCron, delCron} from "../../../../api/cron";
    import {startInterfaceTest} from "../../../../api/common";
    import {getCookie} from "@/utils/cookie";
    import moment from "moment";
    export default {
         created(){
            this.pageInfoIndex = this.$store.state.apiCaseSuitePageInfo.findIndex(i => i.caseSuiteId === this.$route.params.case_suite_id)
            this.size = this.pageInfoIndex === -1 ?
                10: (this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex] && this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex].size) || 10
            this.skip = this.pageInfoIndex === -1 ?
                0: (this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex] && this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex].skip) || 0
            this.sortBy = this.pageInfoIndex === -1 ?
                'createAt': (this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex] && this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex].sortBy) || 'createAt'
            this.order = this.pageInfoIndex === -1 ?
                'descending': (this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex] && this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex].order) || 'descending'
            this.currentPage = this.pageInfoIndex === -1 ?
                1: (this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex] && this.$store.state.apiCaseSuitePageInfo[this.pageInfoIndex].currentPage) || 1
        },
        data() {
            return {
                downloadLink: '',
                downloadName: '',
                filters: {
                    name: ''
                },
                Case: [],
                pageInfoIndex: -1,
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                currentPage: 1,
                totalNum: 0,
                testUrl: '',
                listLoading: false,
                copyLoading: false,
                exportLoading: false,
                sels: [],//列表选中列
                delLoading: false,
                statusChangeLoading: false,
                importLoading: false,
                disDel: true,
                TestStatus: false,
                Host: [],
                hasSels: false,
                editFormVisible: false,//编辑界面是否显示
                editLoading: false,
                editFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    automationGroupLevelFirst: [
                        { type: 'number', required: true, message: '请选择分组', trigger: 'blur'}
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editForm: {
                    name: '',
                    description: ''
                },
                addFormVisible: false,//新增界面是否显示
                addLoading: false,
                addFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    description: [
                        { required: false, message: '请输入版本号', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addForm: {
                    name: '',
                    description: ''
                },
                importExtraData: {
                  projectId: this.$route.params.project_id,
                  userName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                },
            }
        },
        methods: {
            executeTest(){
              let self = this;
              if (self.testUrl) {
                self.listLoading = true;
                self.update = true;
                let ids = self.sels.map(item => item._id);
                let header = {
                  "Content-Type": "application/json",
                };
                let params = JSON.stringify({
                  "domain": self.testUrl,
                  "caseSuiteIdList": ids,
                  "executorNickName": unescape(getCookie('nickName').replace(/\\u/g, '%u')),
                  "executionMode" : "用例组手动执行"
                });
                startInterfaceTest(params, header).then((res) => {
                  self.listLoading = false;
                  self.update = false;
                  let {status, data} = res;
                  if (status === 'ok'){
                    self.$message.success({
                      message: '测试已成功启动，请稍后前往「测试报告」查看报告',
                      center: true,
                    });
                  } else{
                    self.$message.warning({
                      message: data,
                      center: true
                    });
                  }
                  self.getCaseSuites();
                }).catch((error) => {
                  self.$message.error({
                      message: '用例执行异常/超时，请稍后重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                  self.update = false;
                })
              }
              else {
                this.$message({
                  message: '请选择「测试环境」, 在「执行测试」按钮右边哦~',
                  center: true,
                  type: 'warning'
                })
              }
            },
            TestReport(){
                this.$router.push(
                    {
                        name: '测试报告', params:
                            {
                                project_id: this.$route.params.project_id,
                            }
                    });
            },
            getHost() {
              let self = this;
              let header = {};
              let params = {status: true, 'projectId': self.$route.params.project_id};
              getHosts(self.$route.params.project_id, params, header).then((res) => {
                let {status, data} = res
                if (status === 'ok'){
                  self.Host = data.rows
                }
                else{
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              })
            },
            onBeforeUpload(file) {
                let Xls = file.name.split('.');
                if(Xls[1] === 'xls'||Xls[1] === 'xlsx'){
                    return file
                }else {
                    this.$message.warning('只接收 .xls / .xlsx 文件哦 ~ ')
                    return false
                }
            },
            onSuccessUpload(response){
                let self = this;
                let {status, data} = response
                if (status === 'ok'){
                  this.$message.success(data)
                }else {
                  this.$message.error(data)
                }
                self.getCaseSuites()
                self.importLoading = false;
            },
            onProgressUpload(event){
              let self = this;
              self.importLoading = true;
            },
            onErrorUpload(err){
              let self = this;
              self.importLoading = false;
              this.$message.error(err)
            },
            // 获取用例列表
            getCaseSuites() {
                this.listLoading = true;
                let self = this;
                let params = {skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                              projectId: self.$route.params.project_id};
                if (self.filters.name.trim() !== ''){
                  params['name'] = self.filters.name.trim()
                };
                let header = {};
                getCaseSuiteList(self.$route.params.project_id, params, header).then((res) => {
                  self.listLoading = false;
                  let { status, data } = res;
                  if (status === 'ok') {
                    self.Case = data.rows;
                    self.totalNum = data.totalNum;
                  }
                  else {
                    self.$message.error({
                      message: data,
                      center: true,
                    })
                  }
                }).catch((error) => {
                  self.$message.error({
                      message: '用例列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            handleSizeChange(val){
              let self = this;
              self.$store.commit('setApiCaseSuitePageInfo', {size: val, projectId: self.$route.params.project_id})
              self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
              self.size = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].size) || 10
              self.listLoading = true;
              let params = {skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getCaseSuiteList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.Case = data.rows;
                  self.totalNum = data.totalNum;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                self.$message.error({
                    message: '用例列表获取失败，请稍后刷新重试哦~',
                    center: true,
                });
                self.listLoading = false;
              })
            },
            handleCurrentChange(val){
              let self = this;
              self.listLoading = true;
              self.$store.commit('setApiCaseSuitePageInfo', {skip: (val - 1 ) * self.size, projectId: self.$route.params.project_id})
              self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
              self.skip = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].skip) || 0
              self.$store.commit('setApiCaseSuitePageInfo', {currentPage: self.currentPage, projectId: self.$route.params.project_id})
              self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
              let params = {skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getCaseSuiteList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.Case = data.rows;
                  self.totalNum = data.totalNum;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                self.$message.error({
                    message: '用例列表获取失败，请稍后刷新重试哦~',
                    center: true,
                });
                self.listLoading = false;
              })
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then((res) => {
                    this.editLoading = true;
                    //NProgress.start();
                    let self = this;
                    let header = {};
                    let params = {"isDeleted": true}
                    updateCaseSuite(self.$route.params.project_id, row._id, params, header).then((res) => {
                      self.editLoading = false;
                      let { status, data } = res;
                      if (status === 'ok') {
                        self.$message.success({
                          message: '删除成功',
                          center: true,
                        });
                        self.getCaseSuites()
                      }
                      else {
                        self.$message.error({
                          message: data,
                          center: true,
                        })
                        self.getCaseSuites()
                      }
                    }).catch(() => {
                      self.$message.error({
                        message: '删除用例失败,请稍后重试哦',
                        center: true
                      })
                      self.editLoading = false;
                    });
                })
            },
            selsChange: function (sels) {
                if (sels.length>0) {
                    this.sels = sels;
                    this.hasSels = true
                } else {
                    this.hasSels = false
                }
            },
            //批量删除
            batchRemove: function () {

            },
            //显示编辑界面
            handleEdit: function (index, row) {
                this.editFormVisible = true;
                this.editForm = Object.assign({}, this.editForm, row); // 新字段上线，需要使用this.editForm添加
            },
            //显示新增界面
            handleAdd: function () {
                this.addFormVisible = true;
            },
            // 修改用例
            editSubmit: function () {
                let self = this;
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editLoading = true;
                            let params = {
                              name: self.editForm.name,
                              description: self.editForm.description,
                              lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            }
                            let header = {
                              "Content-Type": "application/json",
                              Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
                            };
                            updateCaseSuite(self.$route.params.project_id, self.editForm._id, params, header).then((res) => {
                              self.editLoading = false;
                              let { status, data } = res;
                              if (status === 'ok') {
                                self.editFormVisible = false
                                self.$message.success({
                                  message: '编辑成功',
                                  center: true,
                                });
                                self.getCaseSuites()
                              }
                              else {
                                self.editFormVisible = false
                                self.$message.error({
                                  message: data,
                                  center: true,
                                })
                                self.getCaseSuites()
                              }
                            })
                        }).catch(() => {
                          self.$message.error({
                            message: '编辑用例失败,请稍后重试哦',
                            center: true
                          })
                          self.editFormVisible = false
                        });
                    }
                });
            },
            // 导出用例
            async exportCases(){
              let self = this;
              self.exportLoading = true;
              let caseSuiteIds = self.sels.map(item => item._id);
              let header = {
                  "Content-Type": "application/json"
              };
              let params = JSON.stringify({
                "caseSuiteIds": caseSuiteIds
              });
              exportTestCases(params, header).then((res) => {
                const blob = new Blob([res])
                self.downloadLink = window.URL.createObjectURL(blob)
                self.downloadName = `测试用例_${moment().format('YYYY-MM-DD-HH-mm-ss')}.xlsx`
                self.$nextTick(() => {
                    self.$el.querySelector('.js-download-doc').click()
                    window.URL.revokeObjectURL(this.downloadLink)
                    self.exportLoading = false;
                    self.$message.success({
                      message: '用例导出成功',
                      center: true,
                    });
                })
              }).catch((error) => {
                  console.log(error)
                  self.$message.error({
                      message: '用例导出失败，请稍后重试哦~',
                      center: true,
                  });
                  self.exportLoading = false;
              })
            },
            //新增用例
            addSubmit: function () {
                this.$refs.addForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addLoading = true;
                            let params ={
                                name: self.addForm.name,
                                description: self.addForm.description,
                                creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };
                            let header = {};
                            addCaseSuite(self.$route.params.project_id, params, header).then((res) => {
                              self.addLoading = false;
                              let { status, data } = res;
                              if (status === 'ok') {
                                self.addFormVisible = false
                                self.$message.success({
                                  message: '添加成功',
                                  center: true,
                                });
                                self.$refs['addForm'].resetFields();
                                self.addFormVisible = false;
                                self.getCaseSuites()
                              }
                              else {
                                self.addFormVisible = false
                                self.$message.error({
                                  message: data,
                                  center: true,
                                })
                                self.$refs['addForm'].resetFields();
                                self.addFormVisible = false;
                                self.getCaseSuites()
                              }
                            }).catch(() => {
                              self.$message.error({
                                message: '新增用例失败,请稍后重试哦',
                                center: true
                              })
                              self.addLoading = false;
                            });
                        })
                    }
                });
            },
            copyCaseSuite(index, row){
              let self = this;
              self.copyLoading = true;
              let header = {"Content-Type": "application/json"};
              let params = {};
              copyCaseSuite(self.$route.params.project_id, row._id, params, header).then((res)=>{
                self.copyLoading = false;
                let {status, data} = res;
                if (status === 'ok'){
                  self.$message.success({
                      message: data,
                      center: true,
                  })
                }
                else {
                  self.$message.error({
                      message: data,
                      center: true,
                  })
                }
                self.getCaseSuites()
              }).catch((error) => {
                self.$message.error({
                    message: '用例组复制失败，请稍后重试哦~',
                    center: true,
                });
                self.copyLoading = false;
              })
            },
            //排序
            sortChange (column){
              let self = this;
              self.listLoading = true;
              self.$store.commit('setApiCaseSuitePageInfo',{sortBy: column.prop, projectId: self.$route.params.project_id})
              self.pageInfoIndex = self.$store.state.apiCaseSuitePageInfo.findIndex(i => i.projectId === self.$route.params.project_id)
              self.sortBy = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].sortBy) || 'createAt'
              self.$store.commit('setApiCaseSuitePageInfo',{order: column.order, projectId: self.$route.params.project_id})
              self.order = (self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex] && self.$store.state.apiCaseSuitePageInfo[self.pageInfoIndex].order) || 'descending'
              let params = {skip: self.skip, size: self.size, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getCaseSuiteList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.Case = data.rows;
                  self.totalNum = data.totalNum;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              })
            },
            handleChangeStatus: function(index, row) {
                let self = this;
                self.statusChangeLoading = true;
                let status = !row.status;
                let params = {
                    'status': status
                };
                let headers = {
                    "Content-Type": "application/json",
                };
                updateCaseSuite(this.$route.params.project_id, row._id, params, headers).then(res => {
                    let {status, data} = res;
                    self.statusChangeLoading = false;
                    if (status === 'ok') {
                        self.$message({
                            message: '状态变更成功',
                            center: true,
                            type: 'success'
                        });
                        row.status = !row.status;
                    }
                    else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                    self.getCaseSuites()
                }).catch(() => {
                  self.$message.error({
                    message: '用例组状态更新失败,请稍后重试哦',
                    center: true
                  })
                  self.statusChangeLoading = false;
                  this.getCaseSuites()
                });
            },
            checkActiveEnv: function(){
              let self = this;
              if (self.Host.length < 1){
                self.$message.warning({
                    message: '未找到「启用的测试环境」哦, 请前往「Host配置」进行设置',
                    center: true,
                })
              }
            },
            // 修改table tr行的背景色
            reportRowStyle({ row, rowIndex }){
              if (!(row.status === true))
                return 'background-color: #DDDDDD'
              else {
                return ''
              }
            },
            ReportTableRow({ row, rowIndex }){
              return 'reportTableRow';
            },
        },
        mounted() {
            this.getCaseSuites();
            this.getHost();

        },
        computed: {
           getImportUrl: function() {
              let url = `${process.env.CASE_IMPORT_URI}`
              return url
           }
        }
    }
</script>

<style lang="scss" scoped>
    .api-title {
        padding: 15px;
        margin: 0px;
        text-align: center;
        border-radius:5px;
        font-size: 15px;
        color: aliceblue;
        background-color: rgb(32, 160, 255);
        font-family: PingFang SC;
    }
    .group .editGroup {
        float:right;
    }
    .row-title {
        margin: 35px;
    }
    .addGroup {
        margin-top: 0px;
        margin-bottom: 10px;
        border-radius: 25px;
    }
    .api-view-a {
        margin-left: 15px;
        margin-right: 15px;
        display: block;
    }
    .api-view-b {
        margin-left: 15px;
        margin-right: 15px;
        display: none;
    }
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        margin-left: 35px;
        border-radius: 25px;
    }
    .copyBtn{
      color: #fff;
      background-color: #33CC00;
      border-color: #33CC00;
    }
</style>
