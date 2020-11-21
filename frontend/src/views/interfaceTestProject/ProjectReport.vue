<template>
  <section style="margin:35px">

    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters" @submit.native.prevent>
        <router-link :to="{ name: '接口测试'}" style='text-decoration: none;color: aliceblue;'>
                <el-button round style="margin-left: 35px"><i class="el-icon-d-arrow-left" ></i> 回首页</el-button>
        </router-link>
        <div style="float: right; margin-right: 150px">
          <el-form-item>
            <el-input v-model.trim="filters._id" placeholder="报告编号" @keyup.enter.native="getTestReports"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" class="el-icon-search" @click="getTestReports"> 查询</el-button>
          </el-form-item>
        </div>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table @sort-change='sortChange' :data="testReports" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column sortable='custom' prop="_id" label="报告编号" min-width="17%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="testCount" label="用例总数" min-width="8%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="passCount" label="通过数" min-width="8%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="failedCount" label="失败数" min-width="8%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="passRate" label="通过率" min-width="8%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="comeFrom" label="报告来源" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="executorNickName" label="执行人" min-width="10%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="createAt" label="报告生成时间" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column label="操作" min-width="20%">
        <template slot-scope="scope">
          <el-button size="small" class="el-icon-document" type="primary" @click="showReportDetail(scope.$index, scope.row)"> 查看详情</el-button>
          <el-button size="small" class="el-icon-download" :loading="exportLoading" type="primary" @click="exportReportDetail(scope.$index, scope.row)"> 导出</el-button>
          <!--<el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>-->
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

    <!--报告详情-->
    <el-dialog title="报告详情" width="97%" v-loading="detailLoading" :visible.sync="isReportDetailShow" :close-on-click-modal="false">
      <div style="height:700px;overflow:auto;overflow-x:hidden;border: 1px solid #e6e6e6">
        <el-table height="700" :data="testReportDetail" :row-class-name="reportsTableRow" :header-cell-style="reportHeaderColor" v-loading="listLoading" style="width: 100%;">
          <el-table-column prop="testBaseInfo.name" label="用例名称" min-width="25%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.requestMethod" label="请求方法" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.url" label="请求地址" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.headers" label="请求头" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.cookies" label="请求Cookie" min-width="18%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.presendParams" label="请求参数" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.checkHttpCode" label="状态码校验" min-width="18%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="responseHttpStatusCode" label="实际状态码" min-width="18%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.checkResponseData" label="数据校验" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.checkResponseNumber" label="数值校验" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.checkResponseSimilarity" label="相似度校验" min-width="18%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="responseData" label="实际数据" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testConclusion" label="测试结论" min-width="15%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testStartTime" label="测试开始时间" min-width="25%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="testBaseInfo.checkResponseTime" label="耗时校验/s" min-width="17%" sortable show-overflow-tooltip>
          </el-table-column>
          <el-table-column prop="spendingTimeInSec" label="测试耗时/s" min-width="17%" sortable show-overflow-tooltip>
          </el-table-column>
        </el-table>
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
    import {getReportList, getReportDetail, exportReportDetail} from "../../api/testReport";
    import moment from "moment";
    export default {
        data () {
            return {
                downloadLink: '',
                downloadName: '',
                listLoading: false,
                detailLoading: false,
                exportLoading: false,
                isReportDetailShow: false,
                testReports: [],
                testReportDetail: [],
                sels: [],
                size: 10,
                skip: 0,
                sortBy: 'createAt',
                order: 'descending',
                pageNum: 1,
                totalNum: 0,
                filters: {
                  _id: ''
                },
            }
        },
        mounted(){
          this.getTestReports()
        },
        methods: {
            selsChange: function (sels) {
              this.sels = sels;
            },
            getTestReports() {
                let self = this;
                self.listLoading = true;
                let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
                if (self.filters._id.trim() !== ''){
                  params['_id'] = self.filters._id.trim()
                };
                let header = {};
                getReportList(self.$route.params.project_id, params, header).then((res) => {
                  self.listLoading = false;
                  let {status, data} = res;
                  if (status === 'ok'){
                    self.testReports = data.rows;
                    self.totalNum = data.totalNum;
                  }else {
                    self.$message.error({
                      message: data,
                      center: true,
                    });
                  }
                }).catch((error) => {
                  console.log(error)
                  self.$message.error({
                      message: '测试报告获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            // 导出报告详情
            async exportReportDetail(index, row){
              let self = this;
              self.exportLoading = true;
              let project_id = row.projectId
              let report_id = row._id
              let header = {
                  "Content-Type": "application/json"
              };
              exportReportDetail(project_id, report_id, header).then((res) => {
                const blob = new Blob([res])
                self.downloadLink = window.URL.createObjectURL(blob)
                self.downloadName = `接口测试报告_${moment().format('YYYY-MM-DD-HH-mm-ss')}.xlsx`
                self.$nextTick(() => {
                    self.$el.querySelector('.js-download-doc').click()
                    window.URL.revokeObjectURL(this.downloadLink)
                    self.exportLoading = false;
                    self.$message.success({
                      message: '报告导出成功',
                      center: true,
                    });
                })
              }).catch((error) => {
                  console.log(error)
                  self.$message.error({
                      message: '报告导出失败，请稍后重试哦~',
                      center: true,
                  });
                  self.exportLoading = false;
              })
            },
            showReportDetail(index, row){
              let self = this;
              self.isReportDetailShow = true;
              self.detailLoading = true;
              let header = {};
              getReportDetail(self.$route.params.project_id, row._id , header).then((res) => {
                self.detailLoading = false;
                let {status, data} = res;
                if (status === 'ok'){
                  let testDetails = data["testDetail"] || [];
                  if (testDetails.length) {
                    testDetails.forEach((item, index, array) => {
                      item["testBaseInfo"]["headers"] = JSON.stringify(item["testBaseInfo"]["headers"]) || '';
                      item["testBaseInfo"]["cookies"] = JSON.stringify(item["testBaseInfo"]["cookies"]) || '';
                      item["testBaseInfo"]["presendParams"] = JSON.stringify(item["testBaseInfo"]["presendParams"]) || '';

                      if(item["testBaseInfo"]["presendParams"].length > 5000){
                        item["testBaseInfo"]["presendParams"] = item["testBaseInfo"]["presendParams"].substr(0, 5000) + '......(长度已超出限制，完整请求参数请前往数据库查看)'
                      }

                      // TODO 判断可优化

                      item["responseData"] ?
                       item["responseData"].toString().trim() === '' ?
                        item["responseData"] = '(无任何数据)':
                        item["responseData"] = item["responseData"]:
                       item["responseData"] = '(无任何数据)'

                      if(item["responseData"].length > 5000){
                        item["responseData"] = item["responseData"].substr(0, 5000) + '......(长度已超出限制，完整响应请前往数据库查看)'
                      }

                      if(item["testConclusion"].length > 5000){
                        item["testConclusion"] = item["testConclusion"].substr(0, 5000) + '......(长度已超出限制，完整响应请前往数据库查看)'
                      }

                      item["responseHttpStatusCode"] ?
                       item["responseHttpStatusCode"].toString().trim() === '' ?
                        item["responseHttpStatusCode"] = '(无任何数据)':
                        item["responseHttpStatusCode"] = item["responseHttpStatusCode"]:
                       item["responseHttpStatusCode"] = '(无任何数据)'

                      if (item["testBaseInfo"]["checkResponseData"] === undefined || item["testBaseInfo"]["checkResponseData"] === null || (item["testBaseInfo"]["checkResponseData"].length === 1
                          && item["testBaseInfo"]["checkResponseData"][0]['regex'].trim() === '')){
                        item["testBaseInfo"]["checkResponseData"] = '(无任何校验)'
                      }else{
                        item["testBaseInfo"]["checkResponseData"] = JSON.stringify(item["testBaseInfo"]["checkResponseData"]) || '';
                      }
                      if (item["testBaseInfo"]["checkResponseNumber"] === undefined || item["testBaseInfo"]["checkResponseNumber"] === null || (item["testBaseInfo"]["checkResponseNumber"].length === 1
                          && item["testBaseInfo"]["checkResponseNumber"][0]['expressions']['expectResult'].trim() === '')){
                        item["testBaseInfo"]["checkResponseNumber"] = '(无任何校验)'
                      }else{
                        item["testBaseInfo"]["checkResponseNumber"] = JSON.stringify(item["testBaseInfo"]["checkResponseNumber"]) || '';
                      }
                      if (item["testBaseInfo"]["checkResponseSimilarity"] === undefined || item["testBaseInfo"]["checkResponseSimilarity"] === null || (item["testBaseInfo"]["checkResponseSimilarity"].length === 1
                          && item["testBaseInfo"]["checkResponseSimilarity"][0]['compairedText'].trim() === '')){
                        item["testBaseInfo"]["checkResponseSimilarity"] = '(无任何校验)'
                      }else{
                        item["testBaseInfo"]["checkResponseSimilarity"] = JSON.stringify(item["testBaseInfo"]["checkResponseSimilarity"]) || '';
                      }

                      if (item["testBaseInfo"]["presendParams"] === 'null' || item["testBaseInfo"]["presendParams"] === '{}'){
                        item["testBaseInfo"]["presendParams"] = '(无任何参数)'
                      }
                      if (item["testBaseInfo"]["headers"] === 'null'){
                        item["testBaseInfo"]["headers"] = '(无任何请求头部)'
                      }
                      if (item["testBaseInfo"]["cookies"] === '[]'){
                        item["testBaseInfo"]["cookies"] = '(无任何Cookie)'
                      }
                      if (item["testBaseInfo"]["checkHttpCode"] === null || item["testBaseInfo"]["checkHttpCode"] === undefined){
                        item["testBaseInfo"]["checkHttpCode"] = '(无任何校验)'
                      }
                      if (item["testBaseInfo"]["checkResponseTime"] === null || item["testBaseInfo"]["checkResponseTime"] === undefined){
                        item["testBaseInfo"]["checkResponseTime"] = '(无任何校验)'
                      }
                    });
                  }
                  self.testReportDetail = testDetails
                }else{
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                }
              }).catch((error) => {
                  console.log(error)
                  self.$message.error({
                      message: '报告详情获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.detailLoading = false;
              });
            },
            handleSizeChange(val){
              let self = this;
              self.size = val;
              self.listLoading = true;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                projectId: self.$route.params.project_id};
              let header = {};
              getReportList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let {status, data} = res;
                if (status === 'ok'){
                  self.testReports = data.rows;
                  self.totalNum = data.totalNum;
                }else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '测试报告获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            handleCurrentChange(val){
              let self = this;
              self.skip = (val - 1 ) * self.size;
              self.listLoading = true;
              let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
                            projectId: self.$route.params.project_id};
              let header = {};
              getReportList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let {status, data} = res;
                if (status === 'ok'){
                  self.testReports = data.rows;
                  self.totalNum = data.totalNum;
                }else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '测试报告获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            // 修改table tr行的背景色
            reportsTableRow({ row, rowIndex }){
              if (row.status.toString() === 'ok')
                return 'bg1-row reportsTableRow'
              else {
                return 'bg2-row reportsTableRow'
              }
            },
            // 修改table header的背景色
            reportHeaderColor({ row, column, rowIndex, columnIndex }) {
              if (rowIndex === 0) {
                return 'background-color: #1E90FF;color: #fff;font-weight: 500;'
              }
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
              getReportList(self.$route.params.project_id, params, header).then((res) => {
                self.listLoading = false;
                let {status, data} = res;
                if (status === 'ok'){
                  self.testReports = data.rows;
                  self.totalNum = data.totalNum;
                }else {
                  self.$message.error({
                    message: data,
                    center: true,
                  });
                }
              }).catch((error) => {
                  self.$message.error({
                      message: '测试报告获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            }
        },
        watch: {
            time(){

            }
        }
    }
</script>

<style lang="scss">
  .demo-table-expand {
      font-size: 0;
  }
  .el-tooltip__popper{
    max-width:60%
  }
  .el-table .el-table__body .reportsTableRow:hover>td {
    background-color: deepskyblue;
  }
  .el-table .bg1-row{
    background-color: #33CC00;
    color: #fff;
    font-weight: 500;
  }
  .el-table .bg2-row{
    background-color: #FF3333;
    color: #fff;
    font-weight: 500;
  }
</style>
