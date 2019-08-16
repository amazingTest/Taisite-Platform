<template>
    <section>

        <!--新增界面-->
        <el-dialog width=80% title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" style="width:75%; left: 12.5%">
          <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
            <el-form-item label="用例名称" prop="name">
              <el-input v-model.trim="addForm.name" auto-complete="off"></el-input>
            </el-form-item>
            <el-row :gutter="24">
              <el-col :span="8">
                <el-form-item label="协议" prop='requestProtocol'>
                  <el-select v-model="addForm.requestProtocol" placeholder="请选择">
                    <el-option v-for="item in protocolOptions" :key="item.value" :label="item.label" :value="item.value">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="请求方法" prop='requestMethod'>
                  <el-select v-model="addForm.requestMethod" placeholder="请选择">
                    <el-option v-for="item in methodOptions" :key="item.value" :label="item.label" :value="item.value">
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="接口路由" prop='route'>
                  <el-input v-model.trim="addForm.route" auto-complete="off"></el-input>
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


        <!--工具条-->
        <el-col :span="24" class="toolbar">
          <el-form :inline="true" >
            <router-link :to="{
                    name: '用例列表', params: {
                      project_id: this.$route.params.project_id
                    }
                }" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list"><i class="el-icon-d-arrow-left"return-list style="margin-right: 5px"></i>用例列表</el-button>
            </router-link>
            <el-form-item style="margin-left: 35px">
              <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新建接口用例</el-button>
            </el-form-item>
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
                  <el-button class="el-icon-upload2" :disabled="importLoading" type="primary"> 用例导入</el-button>
                </el-upload>
               </el-tooltip>
            </el-form-item>
            <el-form-item style="margin-left: 5px">
              <el-tooltip class="item" effect="dark" content="导出格式是 xlsx 哦~" placement="top-start">
                <el-button class="el-icon-download" :loading="exportLoading" :disabled="!hasSels" type="primary" @click="exportCases"> 用例导出</el-button>
              </el-tooltip>
            </el-form-item>
            <el-form-item style="float: right; margin-right: 116px">
              <el-select v-model="url" @visible-change='checkActiveEnv' clearable placeholder="测试环境" >
                <el-option
                  v-for="(item,index) in Host"
                  :key="index+''"
                  :label="item.name"
                  :value="item.host">
                </el-option>
              </el-select>
              <el-form-item>
                  <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getCaseApiList"></el-input>
              </el-form-item>
              <el-form-item>
                  <el-button type="primary" class="el-icon-search" @click="getCaseApiList"> 查询</el-button>
              </el-form-item>
            </el-form-item>
          </el-form>
        </el-col>


        <!--列表-->
        <el-table @sort-change='sortChange' @selection-change="selsChange" :data="ApiList" :row-style="reportRowStyle" :row-class-name="ReportTableRow" highlight-current-row v-loading="listLoading" style="width: 100%;">
            <el-table-column type="selection" min-width="5%">
            </el-table-column>
            <el-table-column prop="name" label="接口用例名称" min-width="60%" sortable='custom' show-overflow-tooltip>
                <template slot-scope="scope">
                    <el-icon name="name"></el-icon>
                    <router-link :to="{ name: '修改用例', params: {case_id: scope.row._id}}" style='text-decoration: none;color: #000000;'>{{ scope.row.name }}
                    </router-link>
                </template>
            </el-table-column>
            <el-table-column prop="route" label="接口地址" min-width="30%" sortable='custom' show-overflow-tooltip>
                <template slot-scope="scope">
                    <span class="HttpStatus">{{scope.row.requestMethod}}</span><span style="font-size: 16px">{{scope.row.route}}</span>
                </template>
            </el-table-column>
            <el-table-column prop="description" label="用例描述" min-width="35%" sortable='custom' show-overflow-tooltip>
              <template slot-scope="scope">
                <span>{{scope.row.description}}</span>
              </template>
            </el-table-column>
            <el-table-column prop="createAt" label="创建时间" min-width="35%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="creatorNickName" label="创建者" min-width="25%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="lastUpdateTime" label="最后更新时间" min-width="35%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
             <el-table-column prop="lastUpdatorNickName" label="最后更新人" min-width="28%" sortable='custom' show-overflow-tooltip>
            </el-table-column>
            <el-table-column prop="result" label="测试结果" min-width="25%" sortable='custom' show-overflow-tooltip>
                <template slot-scope="scope">
                    <span v-show="scope.row.lastManualTestResult.status!=='ok'&&scope.row.lastManualTestResult.status!=='failed'&&!scope.row.testStatus">尚无手动测试结果</span>
                    <span v-show="scope.row.testStatus">测试中...</span>
                    <span v-show="!scope.row.testStatus && scope.row.lastManualTestResult.status==='ok'" style="color: #11b95c;cursor:pointer;" @click="resultShow(scope.row)">通过,查看详情</span>
                    <span v-show="!scope.row.testStatus && scope.row.lastManualTestResult.status==='failed'" style="color: #cc0000;cursor:pointer;" @click="resultShow(scope.row)">失败,查看详情</span>
                </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" min-width="17%" sortable='custom'>
                <template slot-scope="scope">
                    <img v-show="scope.row.status" src="../../../../assets/imgs/icon-yes.svg"/>
                    <img v-show="!scope.row.status" src="../../../../assets/imgs/icon-no.svg"/>
                </template>
            </el-table-column>
            <el-table-column label="操作" min-width="110%">
                <template slot-scope="scope">
                    <el-button type="primary" size="small" :loading="testLoading" @click="Test(scope.$index, scope.row)">测试</el-button>
                    <el-button class="copyBtn" size="small" :loading="copyLoading" @click="copyCase(scope.$index, scope.row)">复制</el-button>
                    <el-button
                      type="info"
                      size="small"
                      :loading="statusChangeLoading"
                      @click="handleChangeStatus(scope.$index, scope.row)">
                        {{scope.row.status===false?'启用':'禁用'}}
                    </el-button>
                    <el-button type="danger" size="small" :loading="delLoading" @click="handleDel(scope.$index, scope.row)">删除</el-button>
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

        <!--测试结果-->
        <el-dialog title="测试结果" :visible.sync="TestResult" :close-on-click-modal="false">
            <div style="height:700px;overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6">
                <div style="font-size: 25px;margin-bottom: 10px" class="resultStyle">{{result.name}}</div>
                <div class="lin"></div>
                <div class="resultStyle">请求地址:&nbsp&nbsp{{result.url}}</div>
                <div class="resultStyle">请求方式:&nbsp&nbsp{{result.requestType}}</div>
                <div class="resultStyle" style="padding-bottom: 10px">请求时间:&nbsp&nbsp{{result.testTime}}</div>
                <div class="lin"></div>
                <div style="font-size: 25px;" class="resultStyle">请求头部</div>
                <div v-for="(value, key) in result.headers" class="resultStyle">{{key}}:&nbsp&nbsp{{value}}</div>
                <div v-if="!result.headers || result.headers && Object.keys(result.headers).length <= 0" class="resultStyle">(无任何header)</div>
                <div class="lin" style="margin-top: 10px"></div>
                <div style="font-size: 25px;" class="resultStyle">Cookie</div>
                <div v-for="item in result.cookies" class="resultStyle">{{item.name}}:&nbsp&nbsp{{item.value}}</div>
                <div v-if="!result.cookies || result.cookies && result.cookies.length <= 0 " class="resultStyle">(无任何Cookie)</div>
                <div class="lin" style="margin-top: 10px"></div>
                <div style="font-size: 25px;" class="resultStyle">请求参数</div>
                <div v-for="(value, key) in result.requestParameter" class="resultStyle">{{key}}:&nbsp&nbsp{{value}}</div>
                <div v-if="!result.requestParameter || result.requestParameter && Object.keys(result.requestParameter).length <= 0" class="resultStyle">(无任何请求参数)</div>
                <div class="lin" style="margin-top: 10px"></div>
                <div style="font-size: 25px;" class="resultStyle">预期结果</div>
                <div class="resultStyle">HTTP状态码:&nbsp&nbsp{{result.checkHttpCode}}</div>
                <div class="resultStyle">JSON正则校验:&nbsp&nbsp{{result.checkResponseData}}<span v-show="!result.checkResponseData">无</span></div>
                <div class="resultStyle">JSON数值校验:&nbsp&nbsp{{result.checkResponseNumber}}<span v-show="!result.checkResponseNumber">无</span></div>
                <div class="resultStyle" style="padding-bottom: 10px">JSON智能相似度校验:&nbsp&nbsp{{result.checkResponseSimilarity}}<span v-show="!result.checkResponseSimilarity">无</span></div>
                <div class="lin"></div>
                <div style="font-size: 25px;" class="resultStyle">实际结果</div>
                <div class="resultStyle">HTTP状态码:&nbsp&nbsp{{result.responseHttpStatusCode}}</div>
                <div class="resultStyle">实际返回内容:</div>
                <div v-show="result.responseData" class="resultStyle hljs" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px"><pre>{{result.responseData}}</pre></div>
                <div v-show="!result.responseData" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px;text-align: center">无返回内容</div>
                <div style="font-size: 25px"class="resultStyle">测试总结</div>
                <div v-for="item in result.testConclusion" v-show="result.testConclusion" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px">{{item}}</div>
                <div v-show="!result.testConclusion" class="resultStyle" style="overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6;padding: 10px;width: 90%;word-break: break-all;line-height:25px;text-align: center">无测试结论</div>
            </div>
        </el-dialog>
        <a
            class="js-download-doc"
            :href="downloadLink"
            :download="downloadName"
            v-show="false"
        />
    </section>
</template>

<script>
    import {getCaseList, updateCase, copyCase, importTestCases, exportTestCases, addCase, getLastSingleTestResult} from '../../../../api/testCase';
    import {getHosts} from '../../../../api/host';
    import {startInterfaceTest} from "../../../../api/common";
    import {getCookie} from '@/utils/cookie';
    import moment from "moment";
    export default {
        created(){
            this.pageInfoIndex = this.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === this.$route.params.case_suite_id)
            this.size = this.pageInfoIndex === -1 ?
                10: (this.$store.state.apiCasePageInfo[this.pageInfoIndex] && this.$store.state.apiCasePageInfo[this.pageInfoIndex].size) || 10
            this.skip = this.pageInfoIndex === -1 ?
                0: (this.$store.state.apiCasePageInfo[this.pageInfoIndex] && this.$store.state.apiCasePageInfo[this.pageInfoIndex].skip) || 0
            this.sortBy = this.pageInfoIndex === -1 ?
                'createAt': (this.$store.state.apiCasePageInfo[this.pageInfoIndex] && this.$store.state.apiCasePageInfo[this.pageInfoIndex].sortBy) || 'createAt'
            this.order = this.pageInfoIndex === -1 ?
                'descending': (this.$store.state.apiCasePageInfo[this.pageInfoIndex] && this.$store.state.apiCasePageInfo[this.pageInfoIndex].order) || 'descending'
            this.currentPage = this.pageInfoIndex === -1 ?
                1: (this.$store.state.apiCasePageInfo[this.pageInfoIndex] && this.$store.state.apiCasePageInfo[this.pageInfoIndex].currentPage) || 1
        },
        data() {
            let checkRoute = (rule, value, callback) => {
              if (value !== "" && value !== null){
                if (!value.indexOf('/') != 0){
                  callback()
                } else{
                  callback(new Error('请输入路由(如: /chat)'))
                  this.$message.warning({
                    message: '路由格式不正确!',
                    center: true,
                  });
                }
              }else{
                callback()
              }
            };
            return{
                downloadName: '',
                downloadLink: '',
                protocolOptions: [{ label: "HTTP", value: "HTTP"}, { label: "HTTPS", value: "HTTPS"}],
                methodOptions:[{ label: "GET", value: "GET"},
                               { label: "POST", value: "POST"},
                               { label: "PUT", value: "PUT"},
                               { label: "DELETE", value: "DELETE"},
                               { label: "OPTIONS", value: "OPTIONS"},
                               { label: "PATCH", value: "PATCH"},
                               { label: "HEAD", value: "HEAD"}],
                ApiList: [],
                listLoading: false,
                testLoading: false,
                importLoading: false,
                exportLoading: false,
                copyLoading: false,
                statusChangeLoading: false,
                delLoading: false,
                searchName: "",
                pageInfoIndex: -1,
                size: 10,
                skip: 0,
                hasSels: false,
                sortBy: 'createAt',
                order: 'descending' ,
                currentPage: 1,
                totalNum: 0,
                url: '',
                Host: [],
                apiListLoading: false,
                sels: [],//列表选中列
                TestResult: false,
                result: {},
                addFormVisible: false,
                ApiListLen: "",
                ApiListIndex: 0,
                activeIndex: "",
                //新增界面数据
                addForm: {
                  name: '',
                  description: '',
                  requestProtocol: '',
                  requestMethod: '',
                  route: ''
                },
                addLoading: false,
                addFormRules: {
                  name: [
                    { required: true, message: '请输入名称', trigger: 'blur' },
                    { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
                  ],
                  requestProtocol: [
                    { required: true, message: '请选择类型', trigger: 'blur' }
                  ],
                  requestMethod: [
                    { required: true, message: '请选择类型', trigger: 'blur' }
                  ],
                  route: [
                    { required: true, message: '请输入路由(如:/chat)', trigger: 'blur' },
                    { validator: checkRoute, trigger: 'blur' }
                  ],
                  description: [
                    { required: false, message: '请输入版本号', trigger: 'blur' },
                    { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
                  ]
                },
                filters: {
                  name: ''
                },
                importExtraData: {
                  caseSuiteId: this.$route.params.case_suite_id,
                  projectId: this.$route.params.project_id,
                  userName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                },
            }
        },
        methods: {
            handleSelect(key, keyPath) {
                this.activeIndex = key;
            },
            async getCaseApiList() {
                this.listLoading = true;
                let self = this;
                let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                  projectId: self.$route.params.project_id, caseSuiteId: self.$route.params.case_suite_id};
                if (self.filters.name.trim() !== ''){
                  params['name'] = self.filters.name.trim()
                };
                let header = {};
                getCaseList(self.$route.params.project_id, self.$route.params.case_suite_id, params, header).then((res) => {
                  self.listLoading = false;
                  let { status, data } = res;
                  if (status === 'ok') {
                    self.totalNum = data.totalNum;
                    self.ApiList = data.rows;
                  }
                  else {
                    self.$message.error({
                      message: data,
                      center: true,
                    })
                  }
                }).catch((error) => {
                  self.$message.error({
                      message: '接口用例列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            handleSizeChange(val){
              let self = this;
              self.listLoading = true;
              self.$store.commit('setApiCasePageInfo', {size: val, caseSuiteId: self.$route.params.case_suite_id})
              self.pageInfoIndex = self.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === self.$route.params.case_suite_id)
              self.size = (self.$store.state.apiCasePageInfo[self.pageInfoIndex] && self.$store.state.apiCasePageInfo[self.pageInfoIndex].size) || 10
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id, caseSuiteId: self.$route.params.case_suite_id};
              let header = {};
              getCaseList(self.$route.params.project_id, self.$route.params.case_suite_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.ApiList = data.rows;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '接口用例列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
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
                updateCase(this.$route.params.project_id, this.$route.params.case_suite_id, row._id, params, headers).then(res => {
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
                    self.getCaseApiList()
                }).catch(() => {
                  self.$message.error({
                    message: '用例状态更新失败,请稍后重试哦',
                    center: true
                  })
                  self.statusChangeLoading = false;
                  this.getCaseApiList()
                });
            },
            handleCurrentChange(val){
              let self = this;
              self.listLoading = true;
              self.$store.commit('setApiCasePageInfo', {skip: (val - 1 ) * self.size, caseSuiteId: self.$route.params.case_suite_id})
              self.pageInfoIndex = self.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === self.$route.params.case_suite_id)
              self.skip = (self.$store.state.apiCasePageInfo[self.pageInfoIndex] && self.$store.state.apiCasePageInfo[self.pageInfoIndex].skip) || 0
              self.$store.commit('setApiCasePageInfo', {currentPage: self.currentPage, caseSuiteId: self.$route.params.case_suite_id})
              self.pageInfoIndex = self.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === self.$route.params.case_suite_id)
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id, caseSuiteId: self.$route.params.case_suite_id};
              let header = {};
              getCaseList(self.$route.params.project_id, self.$route.params.case_suite_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.ApiList = data.rows;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '接口用例列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            //排序
            sortChange (column){
              let self = this;
              self.listLoading = true;
              self.$store.commit('setApiCasePageInfo',{sortBy: column.prop, caseSuiteId: self.$route.params.case_suite_id})
              self.pageInfoIndex = self.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === self.$route.params.case_suite_id)
              self.sortBy = (self.$store.state.apiCasePageInfo[self.pageInfoIndex] && self.$store.state.apiCasePageInfo[self.pageInfoIndex].sortBy) || 'createAt';
              self.$store.commit('setApiCasePageInfo',{order: column.order, caseSuiteId: self.$route.params.case_suite_id})
              self.pageInfoIndex = self.$store.state.apiCasePageInfo.findIndex(i => i.caseSuiteId === self.$route.params.case_suite_id)
              self.order = (self.$store.state.apiCasePageInfo[self.pageInfoIndex] && self.$store.state.apiCasePageInfo[self.pageInfoIndex].order) || 'descending';
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                            projectId: self.$route.params.project_id, caseSuiteId: self.$route.params.case_suite_id};
              let header = {};
              getCaseList(self.$route.params.project_id, self.$route.params.case_suite_id, params, header).then((res) => {
                self.listLoading = false;
                let { status, data } = res;
                if (status === 'ok') {
                  self.totalNum = data.totalNum;
                  self.ApiList = data.rows;
                }
                else {
                  self.$message.error({
                    message: data,
                    center: true,
                  })
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '接口用例列表获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            copyCase(index, row){
              let self = this;
              self.copyLoading = true;
              let header = {"Content-Type": "application/json"};
              let params = {};
              copyCase(self.$route.params.project_id, self.$route.params.case_suite_id, row._id, params, header).then((res)=>{
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
                self.getCaseApiList()
              }).catch((error) => {
                self.$message.error({
                    message: '用例复制失败，请稍后重试哦~',
                    center: true,
                });
                self.copyLoading = false;
              })
            },
            Test(index, row) {
                if (this.url) {
                    row.testStatus = true;
                    let self = this;
                    self.testLoading = true;
                    let header = {"Content-Type": "application/json"};
                    let params = {
                            caseIdList: [row._id],
                            domain: self.url,
                            executorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')),
                            executionMode: '单个用例手动执行'
                    };
                    startInterfaceTest(params, header).then((res) => {
                      self.testLoading = false;
                      let {status, data} = res;
                      if (status === 'ok'){
                        self.getCaseApiList()
                        row.testStatus = false;
                      }
                      else {
                          self.$message.warning({
                              message: data,
                              center: true,
                          })
                      }
                      self.getCaseApiList()
                      row.testStatus = false;
                    }).catch((error) => {
                      self.$message.error({
                          message: '用例执行异常/超时，请稍后重试哦~',
                          center: true,
                      });
                      self.testLoading = false;
                      self.getCaseApiList()
                      row.testStatus = false;
                  })
                } else {
                    this.$message({
                        message: '请选择测试环境, 在测试按钮上方哦~',
                        center: true,
                        type: 'warning'
                    })
                }
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
                self.getCaseApiList()
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
            //新增用例
            addSubmit: function () {
              this.$refs.addForm.validate((valid) => {
                if (valid) {
                  let self = this;
                  this.$confirm('确认提交吗？', '提示', {}).then(() => {
                    self.addLoading = true;
                    let params ={
                      name: self.addForm.name,
                      requestProtocol: self.addForm.requestProtocol,
                      requestMethod: self.addForm.requestMethod,
                      route: self.addForm.route,
                      description: self.addForm.description,
                      creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                      lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                    };
                    let header = {};
                    addCase(self.$route.params.project_id, self.$route.params.case_suite_id, params, header).then((res) => {
                      self.addLoading = false;
                      let { status, data } = res;
                      if (status === 'ok') {
                        self.$message.success({
                          message: '保存成功',
                          center: true,
                        });
                        self.$refs['addForm'].resetFields();
                        self.addFormVisible = false;
                        self.getCaseApiList()
                      }
                      else {
                        self.$message.error({
                          message: data,
                          center: true,
                        })
                      }
                    }).catch(() => {
                      self.$message.error({
                        message: '新增接口用例失败,请稍后重试哦',
                        center: true
                      })
                      self.addLoading = false;
                    });
                  });
                }
              });
            },
            async exportCases(){
              let self = this;
              self.exportLoading = true;
              let caseIds = self.sels.map(item => item._id);
              let header = {
                  "Content-Type": "application/json"
              };
              let params = JSON.stringify({
                "testingCaseIds": caseIds
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
            handleDel(index, row){
                this.$confirm('确认删除该记录吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                  let self = this;
                  self.delLoading = true;
                  let params =
                    {
                      isDeleted: true,
                    };
                  let header = {};
                  updateCase(self.$route.params.project_id, self.$route.params.case_suite_id, row._id, params, header).then((res)=>{
                    self.delLoading = false;
                    let {status, data} = res;
                    if (status === 'ok'){
                      self.$message.success({
                        message: '删除成功',
                        center: true
                      })
                      self.getCaseApiList();
                    }else {
                      self.$message.error({
                        message: data,
                        center: true
                      })
                      self.getCaseApiList();
                    }
                  }).catch(() => {
                    self.$message.error({
                      message: '删除失败,请稍后重试哦',
                      center: true
                    })
                    self.delLoading = false;
                  });
               });
            },
            resultShow(row) {
                this.listLoading = true;
                this.result["name"] = row.name;
                this.getResult(row._id);
            },
            getResult(case_id){
                let self = this;
                let header = {"Content-Type": "application/json"};
                getLastSingleTestResult(case_id, header).then((res) => {
                  this.listLoading = false;
                  let {status, data} = res;
                  if (status === 'ok'){
                    self.result["url"] = data.testBaseInfo.url;
                    self.result["requestType"] = data.testBaseInfo.requestMethod;
                    self.result["headers"] = data.testBaseInfo.headers;
                    self.result["cookies"] = data.testBaseInfo.cookies;
                    self.result["requestParameter"] = data.testBaseInfo.presendParams;
                    if (data.testBaseInfo.checkHttpCode){
                      self.result["checkHttpCode"] = data.testBaseInfo.checkHttpCode;
                    }
                    else{
                      self.result["checkHttpCode"] = '无'
                    }
                    // TODO 判断优化
                    if (data.testBaseInfo.checkResponseData  && !(data.testBaseInfo.checkResponseData.length === 1
                          && data.testBaseInfo.checkResponseData[0]['regex'].trim() === '')){

                      self.result["checkResponseData"] = data.testBaseInfo.checkResponseData;
                    }
                    else{
                      self.result["checkResponseData"] = '无'
                    }

                    if (data.testBaseInfo.checkResponseNumber  && !(data.testBaseInfo.checkResponseNumber.length === 1
                          && data.testBaseInfo.checkResponseNumber[0]['expressions']['expectResult'].trim() === '')){

                      self.result["checkResponseNumber"] = data.testBaseInfo.checkResponseNumber;
                    }
                    else{
                      self.result["checkResponseNumber"] = '无'
                    }

                    if (data.testBaseInfo.checkResponseSimilarity  && !(data.testBaseInfo.checkResponseSimilarity.length === 1
                          && data.testBaseInfo.checkResponseSimilarity[0]['compairedText'].trim() === '')){

                      self.result["checkResponseSimilarity"] = data.testBaseInfo.checkResponseSimilarity;
                    }
                    else{
                      self.result["checkResponseSimilarity"] = '无'
                    }

                    //self.result["examineType"] = data.examineType;
                    self.result["result"] = data.status;
                    self.result["responseHttpStatusCode"] = data.responseHttpStatusCode;
                    try{
                      self.result["responseData"] = JSON.parse(data.responseData);
                    }catch(error){
                      self.result["responseData"] = data.responseData;
                    }
                    self.result["testConclusion"] = data.testConclusion;
                    //self.result["responseData"] = JSON.parse(data.responseData.replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false"));
                    self.result["testTime"] = moment(data.testStartTime).format("YYYY年MM月DD日HH时mm分ss秒");
                    self.TestResult = true;
                  }
                  else {
                    self.$message.error({
                      message: data,
                      center: true,
                    })
                  }
                }).catch((error) => {
                  console.log(error)
                  self.$message.error({
                      message: '暂时无法查看报告，请稍后刷新重试~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            getHost() {
                let self = this;
                let header = {};
                let params = {status: true, projectId: self.$route.params.project_id};
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
                }).catch((error) => {
                  self.$message.error({
                      message: '暂时无法获取HOST，请稍后刷新重试~',
                      center: true,
                  });
                })
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
            //显示新增界面
            handleAdd: function () {
              this.addFormVisible = true;
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
                if (sels.length > 0) {
                    this.sels = sels;
                    this.hasSels = true
                } else {
                    this.hasSels = false
                }
            },
            warmPrompt(){
              let self = this;
              let showPrompt = self.$router.history.current.params.showWarmPrompt

              if (showPrompt){
                self.$message.info({
                  message: '测试用例默认按照「创建时间」倒序排序，执行顺序按照「创建时间」正序执行~',
                  center: true,
                })
              }
            },
        },
        mounted() {
            this.getCaseApiList();
            this.getHost();
            this.warmPrompt();
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
    .return-list {
        margin-top: 0px;
        margin-bottom: 10px;
        margin-left: 35px;
        border-radius: 25px;
    }
    .HttpStatus {
        border-radius: 25px;
        padding: 10px;
        box-sizing: border-box;
        color: #fff;
        font-size: 15px;
        background-color: #FF9E1B;
        text-align: center;
        margin-right: 10px;
    }
    .resultStyle{
        margin-left: 2%;
        margin-top: 10px;
        word-wrap: break-word; //文本过长自动换行
    }
    .hljs {
      display: block;
      overflow-x: auto;
      padding: 0.5em;
      background: #333;
      color: white;
    }
    .lin{
        left: 2%;
        border: 1px solid #e6e6e6;
        width: 90%;
        position: relative
    }
    .copyBtn{
      color: #fff;
      background-color: #33CC00;
      border-color: #33CC00;
    }
    pre{
        white-space:pre-wrap;
        white-space:-moz-pre-wrap;
        white-space:-pre-wrap;
        white-space:-o-pre-wrap;
        word-wrap:break-word; /*我是一个很长很长的代码，看我换行了木有？*/
    }
</style>
