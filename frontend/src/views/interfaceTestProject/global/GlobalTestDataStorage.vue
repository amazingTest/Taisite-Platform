<template>
    <div style="margin:35px">
        <!--工具条-->
        <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
            <el-form :inline="true" :model="filters" @submit.native.prevent>
                <router-link :to="{ name: '接口测试'}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="return-list"><i class="el-icon-d-arrow-left"return-list style="margin-right: 5px"></i> 回首页</el-button>
                </router-link>
                <el-form-item style="margin-left: 35px">
                    <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新增数据字典</el-button>
                </el-form-item>
                <div style="float: right; margin-right: 95px">
                  <el-form-item>
                      <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTestDataStorageList"></el-input>
                  </el-form-item>
                  <el-form-item>
                      <el-button type="primary" class="el-icon-search" @click="getTestDataStorageList"> 查询</el-button>
                  </el-form-item>
                </div>
            </el-form>
        </el-col>
        <!--列表-->
        <el-table @sort-change='sortChange' :data="project" :row-style="reportRowStyle" :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
            <el-table-column type="selection" min-width="5%">
            </el-table-column>
            <el-table-column prop="name" label="名称" min-width="30%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="dataMap" label="数据字典" min-width="30%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="35%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="createAt" label="创建时间" min-width="25%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="creatorNickName" label="创建者" min-width="18%" sortable='custom'>
            </el-table-column>
            <el-table-column prop="lastUpdateTime" label="最后更新时间" min-width="25%" sortable='custom' show-overflow-tooltip>
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
                    <el-input placeholder="请输入名称" v-model.trim="editForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="数据字典" prop='dataMap'>
                    <el-input placeholder="请输入数据字典...(如 {'user_id': '123456'})" type="textarea" :rows="5" v-model.trim="editForm.dataMap"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input placeholder="请输入描述..." type="textarea" :rows="5" v-model.trim="editForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
            </div>
        </el-dialog>

        <!--新增界面-->
        <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width: 60%; left: 20%">
            <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
                <el-form-item label="名称" prop="name">
                    <el-input placeholder="请输入名称" v-model.trim="addForm.name" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="数据字典" prop='dataMap'>
                    <el-input placeholder="请输入数据字典...(如 {'user_id': '123456'})" type="textarea" :rows="5" v-model.trim="addForm.dataMap"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop='description'>
                    <el-input placeholder="请输入描述..." type="textarea" :rows="5" v-model.trim="addForm.description"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="addFormVisible = false">取消</el-button>
                <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
            </div>
        </el-dialog>
    </div>
</template>

<script>
    import {getTestDataStorageList, addTestDataStorage, updateTestDataStorage} from '../../../api/testDataStorage';
    import {getCookie} from '@/utils/cookie';
    export default {
        data() {
            let checkJson = (rule, value, callback) => {
              if (value !== "" && value !== null){
                value = value.replace(/'/g, "\"")
                try{
                  value = JSON.parse(value)
                  callback()
                }catch (e) {
                  callback(new Error('参数格式不正确!'))
                  this.$message.warning({
                    message: '参数格式不正确!',
                    center: true,
                  });
                }
              }else{
                callback()
              }
            };
            return {
                filters: {
                    name: ''
                },
                project: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                listLoading: false,
                statusChangeLoading: false,
                sels: [],//列表选中列

                editFormVisible: false,//编辑界面是否显示
                editLoading: false,
                editFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    dataMap: [
                        { required: true, message: '请输入数据字典', trigger: 'blur' },
                        { validator: checkJson, trigger: 'blur' }
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //编辑界面数据
                editForm: {
                    name: '',
                    dataMap: '',
                    description: ''
                },
                addFormVisible: false,//新增界面是否显示
                addLoading: false,
                addFormRules: {
                    name: [
                        { required: true, message: '请输入名称', trigger: 'blur' },
                        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                    ],
                    dataMap: [
                        { required: true, message: '请输入数据字典', trigger: 'blur' },
                        { validator: checkJson, trigger: 'blur' }
                    ],
                    description: [
                        { required: false, message: '请输入描述', trigger: 'blur' },
                        { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                    ]
                },
                //新增界面数据
                addForm: {
                    name: '',
                    dataMap: '',
                    description: ''
                }

            }
        },
        methods: {
            // 获取数据仓库列表
            getTestDataStorageList() {
                this.listLoading = true;
                let self = this;
                let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                  projectId: self.$route.params.project_id};
                if (self.filters.name.trim() !== ''){
                  params['name'] = self.filters.name.trim()
                };
                let header = {};
                getTestDataStorageList(this.$route.params.project_id, params, header).then((res) => {
                    let { status, data } = res;
                    self.listLoading = false;
                    if (status === 'ok') {
                      self.totalNum = data.totalNum;
                      data.rows.forEach(el => {
                          el.dataMap = el.dataMap ? JSON.stringify(el.dataMap) : '(空)'
                      })
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
                      message: '数据仓库列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                });
            },
            handleSizeChange(val){
              let self = this;
              self.size = val;
              self.listLoading = true;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getTestDataStorageList(this.$route.params.project_id, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  data.rows.forEach(el => {
                          el.dataMap = el.dataMap ? JSON.stringify(el.dataMap) : '(空)'
                      })
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
                      message: '数据仓库列表获取失败，请稍后刷新重试哦~',
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
              getTestDataStorageList(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  data.rows.forEach(el => {
                          el.dataMap = el.dataMap ? JSON.stringify(el.dataMap) : '(空)'
                      })
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
                      message: '数据仓库列表获取失败，请稍后刷新重试哦~',
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
              getTestDataStorageList(this.$route.params.project_id, params, header).then((res) => {
                let { status, data } = res;
                self.listLoading = false;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  data.rows.forEach(el => {
                          el.dataMap = el.dataMap ? JSON.stringify(el.dataMap) : '(空)'
                      })
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
                      message: '数据仓库列表获取失败，请稍后刷新重试哦~',
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
                    updateTestDataStorage(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                        self.getTestDataStorageList()
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
                updateTestDataStorage(this.$route.params.project_id, row._id, params, headers).then(res => {
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
                    self.getTestDataStorageList()
                }).catch(() => {
                  self.$message.error({
                    message: 'Host状态更新失败,请稍后重试哦',
                    center: true
                  })
                  self.statusChangeLoading = false;
                  self.getTestDataStorageList()
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
                                dataMap: self.editForm.dataMap,
                                description: self.editForm.description,
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };
                            let headers = {
                                "Content-Type": "application/json",
                            };
                            updateTestDataStorage(this.$route.params.project_id, self.editForm._id, params, headers).then(res => {
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
                                    self.getTestDataStorageList()
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
            //新增
            addSubmit: function () {
                this.$refs.addForm.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            self.addLoading = true;
                            let params = {
                                name: self.addForm.name,
                                dataMap: self.addForm.dataMap,
                                description: self.addForm.description,
                                creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };
                            let header = {
                                "Content-Type": "application/json",
                            };
                            addTestDataStorage(this.$route.params.project_id, params, header).then((res) => {
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
                                    self.getTestDataStorageList()
                                } else {
                                    self.$message.error({
                                        message: data,
                                        center: true,
                                    });
                                    self.$refs['addForm'].resetFields();
                                    self.addFormVisible = false;
                                    self.getTestDataStorageList()
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
                    delHost(headers, params).then(res => {
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
                        self.getTestDataStorageList()
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
            this.getTestDataStorageList();

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
