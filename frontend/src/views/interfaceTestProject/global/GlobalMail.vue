<template>
    <div style="margin:35px">
        <!--工具条-->
        <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
            <el-form :inline="true" :model="filters" @submit.native.prevent>
                <router-link :to="{ name: '接口测试'}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="return-list"><i class="el-icon-d-arrow-left"return-list style="margin-right: 5px"></i> 回首页</el-button>
                </router-link>
                <el-form-item style="margin-left: 35px">
                  <el-button type="primary" class="el-icon-message" @click="handleConfig"> 发件人配置</el-button>
                </el-form-item>
                <el-form-item style="margin-left: 20px">
                    <el-button :disabled="disableAddMails" class="el-icon-plus" type="primary" @click="handleAdd"> 新增接收邮箱</el-button>
                </el-form-item>
                <div style="float: right; margin-right: 145px">
                  <el-form-item>
                      <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getGlobalMail"></el-input>
                  </el-form-item>
                  <el-form-item>
                      <el-button type="primary" class="el-icon-search" @click="getGlobalMail"> 查询</el-button>
                  </el-form-item>
                </div>
            </el-form>
        </el-col>
        <!--列表-->
        <el-table @sort-change='sortChange' :data="project" :row-style="reportRowStyle" :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
            <el-table-column type="selection" min-width="5%">
            </el-table-column>
            <el-table-column prop="name" label="名称" min-width="16%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="mailAddress" label="邮箱地址" min-width="28%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="27%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="createAt" label="创建时间" min-width="23%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="creatorNickName" label="创建者" min-width="18%" sortable='custom'>
            </el-table-column>
            <el-table-column prop="lastUpdateTime" label="最后更新时间" min-width="23%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="lastUpdatorNickName" label="最后更新人" min-width="18%" sortable='custom'>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
                <template slot-scope="scope">
                    <img v-show="scope.row.status" src="../../../assets/imgs/icon-yes.svg"/>
                    <img v-show="!scope.row.status" src="../../../assets/imgs/icon-no.svg"/>
                </template>
            </el-table-column>
            <el-table-column label="操作" min-width="50%">
                <template slot-scope="scope">
                    <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
                    <el-button
                      type="info"
                      size="small"
                      :loading="statusChangeLoading"
                      @click="handleChangeStatus(scope.$index, scope.row)">
                        {{scope.row.status===false?'启用':'禁用'}}
                    </el-button>
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
          :page-sizes="[10, 20, 40]"
          :page-size="size"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalNum">
        </el-pagination>
      </el-col>

        <!--编辑界面-->
        <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
            <el-form :model="editForm"  :rules="editFormRules" ref="editForm" label-width="80px">
                <el-form-item label="名称" prop="name">
                    <el-input v-model.trim="editForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="邮箱地址" prop='mailAddress'>
                    <el-input v-model.trim="editForm.mailAddress" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="5" v-model.trim="editForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary"  @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--新增界面-->
        <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
            <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model.trim="addForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="邮箱地址" prop='mailAddress'>
                    <el-input v-model.trim="addForm.mailAddress" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input type="textarea" :rows="5" v-model.trim="addForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="addFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--配置界面-->
        <el-dialog title="发件人配置" :visible.sync="ConfigFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
          <el-form :inline="true" :model="ConfigForm" label-width="100px" :rules="ConfigFormRules" ref="ConfigForm">
            <el-form-item label="发件人邮箱" prop="username">
              <el-input v-model.trim="ConfigForm.username" auto-complete="off"></el-input>
            </el-form-item>
            <el-form-item label="邮箱授权码" prop='password'>
              <el-input type="password" v-model.trim="ConfigForm.password" auto-complete="off"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button :disabled="isMailSenderChecked" type="info" @click.native="testMailSender" :loading="testMailSenderLoading">请先验证</el-button>
            </el-form-item>
          </el-form>
          <div slot="footer" class="dialog-footer">
            <el-button @click.native="ConfigFormVisible = false">取消</el-button>
            <el-button type="primary" :disabled="!isMailSenderChecked" @click.native="ConfigSubmit" :loading="ConfigLoading">提交</el-button>
          </div>
        </el-dialog>

    </div>
</template>

<script>
    import {getMails, addMail, updateMail} from '../../../api/mail';
    import {getMailSender, addMailSender, updateMailSender, testMailSender} from '../../../api/mailSender';
    import {getCookie} from '@/utils/cookie';
    export default {
        data() {
            var checkMail = (rule, value, callback) => {
                if (!this.isValidMail(value)) {
                    return callback(new Error('邮箱地址格式错误'));
                } else {
                    return callback()
                }
            };
            return {
                filters: {
                    name: ''
                },
                project: [], //指代Mails
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                testMailSenderLoading: false,
                isMailSenderChecked: false,
                sels: [],//列表选中列
                disableAddMails: true,
                editFormVisible: false,//编辑界面是否显示
                editLoading: false,
                editFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    mailAddress: [
                        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
                        { validator: checkMail, trigger: 'blur' }
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editForm: {
                    name: '',
                    mailAddress: '',
                    description: ''
                },
                addFormVisible: false,//新增界面是否显示
                addLoading: false,
                addFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    mailAddress: [
                        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
                        { validator: checkMail, trigger: 'blur' }
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addForm: {
                    name: '',
                    mailAddress: '',
                    description: ''
                },
                ConfigFormVisible: false,//新增界面是否显示
                ConfigLoading: false,
                ConfigFormRules: {
                  username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { validator: checkMail, trigger: 'blur' }
                  ],
                  password: [
                    { required: true, message: '请输入授权码', trigger: 'blur' }
                  ],
                },
                //配置界面数据
                ConfigForm: {
                  username: '',
                  password: '',
                },

            }
        },
        methods: {
            // IP格式验证
            isValidMail(mailAddress) {
                let strRegex = "^[a-z0-9]+([._\\-]*[a-z0-9])*@([a-z0-9]+[-a-z0-9]*[a-z0-9]+.){1,63}[a-z0-9]+$";
                let re = new RegExp(strRegex);
                return re.test(mailAddress);
            },
            // 获取Mail列表
            getGlobalMail() {
                this.listLoading = true;
                let self = this;
                let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                  projectId: self.$route.params.project_id};
                if (self.filters.name.trim() !== ''){
                  params['name'] = self.filters.name.trim()
                };
                let header = {};
                getMails(this.$route.params.project_id, params, header).then((res) => {
                    let { status, data } = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                      self.totalNum = data.totalNum;
                      self.project = data.rows
                    }
                    else {
                        self.$message.error({
                            message: data,
                            center: true,
                        })
                    }
                }).catch((error) => {
                  self.$message.error({
                      message: '邮箱列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            // 获取MailSender
            getMailSender() {
              this.listLoading = true;
              let self = this;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getMailSender(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  if (data.rows.length > 0){
                    self.ConfigForm = data.rows[0];
                    self.disableAddMails = false;
                  }
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '发件人邮箱获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            testMailSender(){
              this.testMailSenderLoading = true;
              let self = this;
              let params = {
                  username: self.ConfigForm.username,
                  password: self.ConfigForm.password,
              };
              let header = {};
              testMailSender(params, header).then((res) => {
                let { status, data } = res;
                self.testMailSenderLoading = false;
                if (status === 'ok') {
                  self.$message.success({
                      message: data,
                      center: true,
                  });
                  self.isMailSenderChecked = true;
                }else {
                  self.$message.warning({
                      message: data,
                      center: true,
                  });
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '发件人邮箱测试失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.testMailSenderLoading = false;
                });
            },
            handleSizeChange(val){
              let self = this;
              self.size = val;
              self.listLoading = true;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getMails(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.project = data.rows
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '邮箱列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            handleCurrentChange(val){
              let self = this;
              self.skip = (val - 1 ) * self.size;
              self.listLoading = true;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getMails(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.project = data.rows
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '邮箱列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            //排序
            sortChange (column){
              let self = this;
              self.listLoading = true;
              self.sortBy = column.prop;
              self.order = column.order;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getMails(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.project = data.rows
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '邮箱列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            //删除
            handleDel: function (index, row) {
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let self = this;
                    let params = {
                      'isDeleted': true
                    };
                    let headers = {
                        "Content-Type": "application/json",
                    };
                    updateMail(this.$route.params.project_id, row._id, params, headers).then(res => {
                        let { status, data } = res;
                        if (status === 'ok') {
                            self.$message({
                                message: '删除成功',
                                center: true,
                                type: 'success'
                            })
                        } else {
                            self.$message.error({
                                message: data,
                                center: true,
                            })
                        }
                        self.getGlobalMail()
                    });
                });
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
                updateMail(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                    self.getGlobalMail()
                }).catch(() => {
                    self.$message.error({
                      message: '接收邮箱状态更新失败,请稍后重试哦',
                      center: true
                    })
                    self.statusChangeLoading = false;
                    self.getGlobalMail()
                });
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
            //显示配置邮箱界面
            handleConfig: function () {
              this.isMailSenderChecked = false;
              this.ConfigFormVisible = true;
            },
            //编辑
            editSubmit: function () {
                let self = this;
                this.$refs.editForm.validate((valid) => {
                    if (valid) {
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.editLoading = true;
                            //NProgress.start();
                            let params = {
                                project_id: this.$route.params.project_id,
                                name: self.editForm.name,
                                mailAddress: self.editForm.mailAddress,
                                description: self.editForm.description,
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            updateMail(this.$route.params.project_id, self.editForm._id, params, headers).then(res => {
                                let {status, data} = res;
                                self.editLoading = false;
                                if (status === 'ok') {
                                    self.$message({
                                        message: '修改成功',
                                        center: true,
                                        type: 'success'
                                    });
                                    self.$refs['editForm'].resetFields();
                                    self.editFormVisible = false;
                                    self.getGlobalMail()
                                } else {
                                    self.$message.error({
                                        message: data,
                                        center: true,
                                    })
                                }
                            })
                        });
                    }
                });
            },
            //配置发件人
            ConfigSubmit:function () {
              this.$refs.ConfigForm.validate((valid) => {
                if (valid) {
                  let self = this;
                  this.$confirm('确认提交吗？', '提示', {}).then(() => {
                    self.ConfigLoading = true;
                    let params = {
                      username: self.ConfigForm.username,
                      password: self.ConfigForm.password,
                      creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                      lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                    };
                    let header = {
                      "Content-Type": "application/json",
                    };
                    addMailSender(this.$route.params.project_id, params, header).then((res) => {
                      let {status, data} = res;
                      self.ConfigLoading = false;
                      if (status === 'ok') {
                        self.$message({
                          message: '配置成功',
                          center: true,
                          type: 'success'
                        });
                        self.$refs['ConfigForm'].resetFields();
                        self.ConfigFormVisible = false;
                        self.getMailSender()
                      } else {
                        self.$message.error({
                          message: data,
                          center: true,
                        });
                        self.$refs['ConfigForm'].resetFields();
                        self.ConfigFormVisible = false;
                        self.getMailSender()
                      }
                    })
                  });
                }
              });
            },
            //新增
            addSubmit: function () {
                this.$refs.addForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addLoading = true;
                            let params = {
                                name: self.addForm.name,
                                mailAddress: self.addForm.mailAddress,
                                description: self.addForm.description,
                                creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };
                            let header = {
                                "Content-Type": "application/json",
                            };
                            addMail(this.$route.params.project_id, params, header).then((res) => {
                                let {status, data} = res;
                                self.addLoading = false;
                                if (status === 'ok') {
                                    self.$message({
                                        message: '添加成功',
                                        center: true,
                                        type: 'success'
                                    });
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;
                                    self.getGlobalMail()
                                } else {
                                    self.$message.error({
                                        message: data,
                                        center: true,
                                    });
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;
                                    self.getGlobalMail()
                                }
                            })
                        });
                    }
                });
            },
            selsChange: function (sels) {
                this.sels = sels;
            },
            //批量删除
            batchRemove: function () {
                let ids = this.sels.map(item => item.id);
                let self = this;
                this.$confirm('确认删除选中记录吗？', '提示', {
                    type: 'warning'
                }).then(() => {
                    self.listLoading = true;
                    //NProgress.start();
                    let params = {
                        project_id: Number(this.$route.params.project_id),
                        ids: ids
                    };
                    let headers = {
                        "Content-Type": "application/json",
                        Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
                    };
                    delMail(headers, params).then(res => {
                        let {msg, code, data} = res;
                        self.listLoading = false;
                        if (code === '999999') {
                            self.$message({
                                message: '删除成功',
                                center: true,
                                type: 'success'
                            })
                        }
                        else {
                            self.$message.error({
                                message: msg,
                                center: true,
                            })
                        }
                        self.getGlobalMail()
                    })
                })
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
            this.getGlobalMail();
            this.getMailSender();
        },
        watch: {
          ConfigForm:{
            handler(curVal, oldVal){
              let self = this
              self.isMailSenderChecked = false;
            },
            deep:true
          }
        }
    }

</script>
<style  lang="scss" scoped>
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        margin-left: 35px;
        border-radius: 25px;
    }
</style>
