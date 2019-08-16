<template>
  <section>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <el-form-item>
          <el-input v-model="filters.name" placeholder="项目名称" @keyup.enter.native="getProjectList"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-search" @click="getProjectList"> 查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="el-icon-plus" @click="handleAdd"> 新增项目</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table @sort-change='sortChange' :data="project" :row-style="reportRowStyle" :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="项目名称" min-width="18%" sortable='custom' show-overflow-tooltip>
        <template slot-scope="scope">
          <el-icon name="name"></el-icon>
          <router-link :to="{ name: '用例列表', params: {project_id: scope.row._id}}" style='text-decoration: none;color: #000000;'>
            {{ scope.row.name }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="项目版本" min-width="18%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="description" label="项目描述" min-width="28%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="22%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="creatorNickName" label="创建者" min-width="22%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="最后更新时间" min-width="22%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="lastUpdatorNickName" label="最后更新人" min-width="22%" sortable='custom'>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="13%" sortable>
        <template slot-scope="scope">
          <img v-show="scope.row.status" src="../../assets/imgs/icon-yes.svg"/>
          <img v-show="!scope.row.status" src="../../assets/imgs/icon-no.svg"/>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="50%">
        <template slot-scope="scope">
          <el-button type="primary" size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
          <el-button type="info" size="small" @click="handleChangeStatus(scope.$index, scope.row)">{{scope.row.status===false?'启用':'禁用'}}</el-button>
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
    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false" style="width: 75%; left: 12.5%">
      <el-form :model="editForm" label-width="80px"  :rules="editFormRules" ref="editForm">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="editForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="版本号" prop='version'>
              <el-input v-model="editForm.version" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="6" v-model="editForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="editFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--新增界面-->
    <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width: 75%; left: 12.5%">
      <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model.trim="addForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="版本号" prop='version'>
              <el-input v-model.trim="addForm.version" auto-complete="off"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述" prop='description'>
          <el-input type="textarea" :rows="6" v-model="addForm.description"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="addFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
  //import NProgress from 'nprogress'
  import {getProjects,  updateProject, addProject} from '../../api/project';
  import {getCookie} from '@/utils/cookie';
  // import ElRow from "element-ui/packages/row/src/row";
  export default {
    // components: {ElRow},
    data() {
      return {
        projectTestType: "interfaceTest",
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
        sels: [],//列表选中列

        editFormVisible: false,//编辑界面是否显示
        editLoading: false,
        options: [{ label: "Web", value: "Web"}, { label: "App", value: "App"}],
        editFormRules: {
          name: [
            { required: true, message: '请输入名称', trigger: 'blur' },
            { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
          ],
          version: [
            { required: true, message: '请输入版本号', trigger: 'blur' },
            { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
          ],
          description: [
            { required: false, message: '请输入描述', trigger: 'blur' },
            { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
          ]
        },
        //编辑界面数据
        editForm: {
          name: '',
          version: '',
          description: ''
        },

        addFormVisible: false,//新增界面是否显示
        addLoading: false,
        addFormRules: {
          name: [
            { required: true, message: '请输入名称', trigger: 'blur' },
            { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
          ],
          version: [
            { required: true, message: '请输入版本号', trigger: 'blur' },
            { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' }
          ],
          description: [
            { required: false, message: '请输入版本号', trigger: 'blur' },
            { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
          ]
        },
        //新增界面数据
        addForm: {
          name: '',
          version: '',
          description: ''
        }

      }
    },
    methods: {
      // 获取项目列表
      getProjectList() {
        this.listLoading = true;
        let self = this;
        let params = { size: self.size, skip: self.skip,  sortBy: self.sortBy, order: self.order,
                         projectTestType: self.projectTestType};
        if (self.filters.name.trim() !== ''){
          params['name'] = self.filters.name.trim()
        };
        let header = {};
        getProjects(params, header).then((res) => {
          self.listLoading = false;
          let { status, data } = res;
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
              message: '项目获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      //删除
      handleDel: function (index, row) {
        this.$confirm('确认删除该记录吗?', '提示', {
          type: 'warning'
        }).then(() => {
          this.listLoading = true;
          let self = this;
          let params = {isDeleted: true};
          let header = {
            "Content-Type": "application/json",
            Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
          };
          updateProject(row._id, params, header).then(_data => {
            let {status, data} = _data;
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
            self.getProjectList()
          });
        })
      },
      handleSizeChange(val){
        let self = this;
        self.size = val;
        self.listLoading = true;
        let params = { size: self.size, skip: self.skip,  sortBy: self.sortBy, order: self.order,
           projectTestType: self.projectTestType};
        let header = {};
        getProjects(params, header).then((res) => {
          self.listLoading = false;
          let { status, data } = res;
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
              message: '项目获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      handleCurrentChange(val){
        let self = this;
        self.skip = (val - 1 ) * self.size;
        self.listLoading = true;
        let params = { size: self.size, skip: self.skip,  sortBy: self.sortBy, order: self.order,
           projectTestType: self.projectTestType};
        let header = {};
        getProjects(params, header).then((res) => {
          self.listLoading = false;
          let { status, data } = res;
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
              message: '项目获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      //排序
      sortChange (column){
        let self = this;
        self.listLoading = true;
        self.sortBy = column.prop;
        self.order = column.order;
        let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order, projectTestType: self.projectTestType};
        let header = {};
        getProjects(params, header).then((res) => {
          self.listLoading = false;
          let { status, data } = res;
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
              message: '项目获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      // 改变项目状态
      handleChangeStatus: function(index, row) {
        let self = this;
        this.listLoading = true;

        let header = {
          "Content-Type": "application/json",
          Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
        };
        if (row.status) {
          let params = { status: false};
          updateProject(row._id, params, header).then(_data => {
            let {status, data} = _data;
            if (status === 'ok') {
              self.$message({
                message: '状态变更成功',
                center: true,
                type: 'success'
              })
            } else {
              self.$message.error({
                message: data,
                center: true,
              })
            }
            self.getProjectList()
          });
        } else {
          let params = { status: true};
          updateProject(row._id, params, header).then(_data => {
            let {status, data} = _data;
            if (status === 'ok') {
              self.$message({
                message: '状态变更成功',
                center: true,
                type: 'success'
              })
            } else {
              self.$message.error({
                message: data,
                center: true,
              })
            }
            self.getProjectList()
          });
        }
      },
      //显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true;
        this.editForm = Object.assign({}, this.editForm, row);
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
                name: self.editForm.name,
                version: self.editForm.version,
                description: self.editForm.description,
                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
              };
              let header = {
                "Content-Type": "application/json",
                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
              };
              updateProject(self.editForm._id, params, header).then(_data => {
                let {status, data} = _data;
                self.editLoading = false;
                if (status === 'ok') {
                  self.$message({
                    message: '修改成功',
                    center: true,
                    type: 'success'
                  });
                  self.$refs['editForm'].resetFields();
                  self.editFormVisible = false;
                  self.getProjectList()
                }else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              });
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
              //NProgress.start();
              let params = JSON.stringify({
                name: self.addForm.name,
                projectTestType: self.projectTestType,
                version: self.addForm.version,
                description: self.addForm.description,
                creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
              });
              let header = {
                "Content-Type": "application/json",
                Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
              };
              addProject(params, header).then(res => {
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
                  self.getProjectList()
                }else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                  self.$refs['addForm'].resetFields();
                  self.addFormVisible = false;
                  self.getProjectList()
                }
              })
            });
          }
        });
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
          this.listLoading = true;
          //NProgress.start();
          let self = this;
          let params = {ids: ids};
          let header = {
            "Content-Type": "application/json",
            Authorization: 'Token ' + JSON.parse(sessionStorage.getItem('token'))
          };
          delProject(header, params).then(_data => {
            let {msg, code, data} = _data;
            if (code === '999999') {
              self.$message({
                message: '删除成功',
                center: true,
                type: 'success'
              })
            } else {
              self.$message.error({
                message: msg,
                center: true,
              })
            }
            self.getProjectList()
          });
        })
      }
    },
    mounted() {
      this.getProjectList();
    }
  }

</script>

<style  lang="scss" scoped>
  .el-table .el-table__body .reportTableRow:hover>td {
    background-color: #F2F2F2;
  }
</style>
