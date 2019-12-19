<template>
  <section style="margin:35px">
    <!--工具条-->
      <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
          <el-form :inline="true" :model="filters" @submit.native.prevent>
              <router-link :to="{ name: '接口测试'}" style='text-decoration: none;color: aliceblue;'>
                    <el-button class="return-list"><i class="el-icon-d-arrow-left"return-list style="margin-right: 5px"></i> 回首页</el-button>
              </router-link>
              <el-form-item style="margin-left: 35px">
                    <el-button class="el-icon-plus" type="primary" @click="handleAdd"> 新增定时任务</el-button>
              </el-form-item>
              <div style="float: right; margin-right: 100px">
                <el-form-item>
                    <el-input v-model.trim="filters.name" placeholder="名称" @keyup.enter.native="getTask"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" class="el-icon-search" @click="getTask"> 查询</el-button>
                </el-form-item>
              </div>
          </el-form>
      </el-col>


    <!--定时任务列表-->
    <el-table @sort-change='sortChange' :row-style="reportRowStyle" :row-class-name="ReportTableRow" :data="crons" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
      <el-table-column type="selection" min-width="5%">
      </el-table-column>
      <el-table-column prop="name" label="定时任务名称" min-width="30%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="35%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="createAt" label="创建时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="creatorNickName" label="创建者" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="lastUpdateTime" label="最后更新时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column sortable='custom' prop="lastUpdatorNickName" label="最后更新人" min-width="15%" show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="next_run_time" label="下一次执行时间" min-width="25%" sortable='custom' show-overflow-tooltip>
      </el-table-column>
      <el-table-column prop="status" label="状态" min-width="10%" sortable='custom'>
        <template slot-scope="scope">
          <img v-show="scope.row.status!=='PAUSED'" src="../../../../assets/imgs/icon-yes.svg"/>
          <img v-show="scope.row.status==='PAUSED'" src="../../../../assets/imgs/icon-no.svg"/>
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
              {{scope.row.status==='PAUSED'?'启动':'停用'}}
          </el-button>
        </template>
      </el-table-column>
    </el-table>


    <!--编辑-->
    <el-dialog title="编辑" :visible.sync="editFormVisible" width="70%" :close-on-click-modal="false" style="width: 65%; left: 17.5%">
      <el-form :model="editForm"  :rules="editFormRules" ref="editForm" label-width="80px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model.trim="editForm.name" auto-complete="off"></el-input>
        </el-form-item>

        <el-form-item label="用例组" prop="testCaseSuiteIdList">
          <el-select
            style="width: 60%;"
            v-model="editForm.testCaseSuiteIdList"
            @visible-change="checkActiveCaseSuite"
            clearable
            multiple
            auto-complete="off">
              <el-option v-for="(item,index) in Case" :key="index+''" :label="item.name" :value="item._id"></el-option>
          </el-select>
          <el-checkbox style="margin-left: 50px" label='是否执行禁用的用例(组)' v-model="editForm.isExecuteForbiddenedCase">
          </el-checkbox>
        </el-form-item>
        <el-form-item label="测试环境" prop="testDomain">
          <el-select
            v-model="editForm.testDomain"
            @visible-change="checkActiveEnv"
            clearable
            auto-complete="off">
              <el-option v-for="(item,index) in Host" :key="index" :label="item.name" :value="item.host"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="触发类型" prop="triggerType">
          <el-select clearable v-model.trim="editForm.triggerType" @change="editFormTriggerTypeChange" auto-complete="off">
            <el-option v-for="(item,index) in TriggerTypes" :key="index+''" :label="item.name" :value="item.value"></el-option>
          </el-select>
        </el-form-item>

       <transition name="el-zoom-in-top">
        <div
            class="form-item-sub form-item-short"
            v-if="editForm.triggerType.toString()==='interval' ||
                  editForm.triggerType.toString()==='date'">
          <el-form-item v-show="editForm.triggerType.toString()==='interval'" label="间隔/秒" prop="interval">
            <el-input style="width:50%" v-model.trim="editForm.interval" type="number" auto-complete="off"></el-input>
          </el-form-item>

          <el-form-item v-show="editForm.triggerType.toString()==='date'" label="具体日期" prop="runDate">
            <el-date-picker
             :picker-options="pickerOptions"
             v-model.trim="editForm.runDate"
             type="datetime"
             placeholder="请选择触发日期">
            </el-date-picker>
          </el-form-item>
         </div>
        </transition>

        <el-form-item label="钉钉提醒">
            <el-radio
                v-model="editForm.isDingDingNotify"
                :label="true">
                是
            </el-radio>
            <el-radio
                v-model="editForm.isDingDingNotify"
                :label="false">
                否
            </el-radio>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div
              class="form-item-sub form-item-short"
              v-if="editForm.isDingDingNotify && editForm.isDingDingNotify.toString()==='true'">
            <el-form-item
               style="width:90%"
               label="钉钉Token"
               prop="dingdingAccessToken">
              <el-input placeholder="如: 52597c9b583090fd397493626c035064f03aaf92669f032d215fde67e43a807e" v-model.trim="editForm.dingdingAccessToken" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-show="editForm.isDingDingNotify.toString()==='true'" label="提醒策略">
                <el-checkbox
                    v-model="editForm.dingdingNotifyStrategy.success"
                    label="测试全通过时提醒">
                </el-checkbox>
                <el-checkbox
                    v-model="editForm.dingdingNotifyStrategy.fail"
                    label="测试存在失败时提醒">
                </el-checkbox>
            </el-form-item>
          </div>
        </transition>

        <el-form-item label="企微提醒">
            <el-radio
                v-model="editForm.isEnterpriseWechatNotify"
                :label="true">
                是
            </el-radio>
            <el-radio
                v-model="editForm.isEnterpriseWechatNotify"
                :label="false">
                否
            </el-radio>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div
              class="form-item-sub form-item-short"
              v-if="editForm.isEnterpriseWechatNotify && editForm.isEnterpriseWechatNotify.toString()==='true'">
            <el-form-item
               style="width:90%"
               label="企微Token"
               prop="enterpriseWechatAccessToken">
              <el-input placeholder="如: 618311c0-yd0f-37e0-b11d-9f7c521d8gb9" v-model.trim="editForm.enterpriseWechatAccessToken" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-show="editForm.isEnterpriseWechatNotify.toString()==='true'" label="提醒策略">
                <el-checkbox
                    v-model="editForm.enterpriseWechatNotifyStrategy.success"
                    label="测试全通过时提醒">
                </el-checkbox>
                <el-checkbox
                    v-model="editForm.enterpriseWechatNotifyStrategy.fail"
                    label="测试存在失败时提醒">
                </el-checkbox>
            </el-form-item>
          </div>
        </transition>

        <el-form-item label="告警邮箱" prop="alarmMailList">
          <el-select
            style="width: 60%;"
            v-model="editForm['alarmMailList']"
            @visible-change="checkActiveMailList"
            clearable
            multiple
            placeholder="请选择告警报告接受者(可多选)">
              <el-option v-for="(item,index) in alarmMailList" :key="index" :label="item.name" :value="item.mailAddress"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="任务描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model.trim="editForm.description"></el-input>
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="editFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="editTask" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--新增界面-->
    <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false" width="70%" style="width: 65%; left: 17.5%">
      <el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model.trim="addForm.name" auto-complete="off"></el-input>
        </el-form-item>

        <el-form-item label="用例组" prop="testCaseSuiteIdList">
          <el-select  style="width: 60%;" clearable v-model="addForm.testCaseSuiteIdList" @visible-change="checkActiveCaseSuite" multiple auto-complete="off">
            <el-option v-for="(item,index) in Case" :key="index+''" :label="item.name" :value="item._id"></el-option>
          </el-select>
          <el-checkbox style="margin-left: 50px" label='是否执行禁用的用例(组)' v-model="addForm.isExecuteForbiddenedCase">
          </el-checkbox>
        </el-form-item>
        <el-form-item label="测试环境" prop="testDomain">
          <el-select clearable v-model="addForm.testDomain" @visible-change="checkActiveEnv" auto-complete="off">
            <el-option v-for="(item,index) in Host" :key="index" :label="item.name" :value="item.host"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="触发类型" prop="triggerType">
          <el-select clearable v-model.trim="addForm.triggerType" auto-complete="off" @change="addFormTriggerTypeChange">
            <el-option v-for="(item,index) in TriggerTypes" :key="index+''" :label="item.name" :value="item.value"></el-option>
          </el-select>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div
              class="form-item-sub form-item-short"
              v-if="addForm.triggerType.toString()==='interval' ||
                    addForm.triggerType.toString()==='date'">
            <el-form-item v-if="addForm.triggerType.toString()==='interval'" label="间隔/秒" prop="interval">
              <el-input v-model.trim="addForm.interval" style="width:50%" type="number" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-if="addForm.triggerType.toString()==='date'" label="具体日期" prop="runDate">
              <el-date-picker
               v-model.trim="addForm.runDate"
               :picker-options="pickerOptions"
               type="datetime"
               placeholder="请选择触发日期">
              </el-date-picker>
            </el-form-item>
          </div>
        </transition>

        <el-form-item label="钉钉提醒">
            <el-radio
                v-model="addForm.isDingDingNotify"
                :label="true">
                是
            </el-radio>
            <el-radio
                v-model="addForm.isDingDingNotify"
                :label="false">
                否
            </el-radio>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div
              class="form-item-sub form-item-short"
              v-if="addForm.isDingDingNotify && addForm.isDingDingNotify.toString()==='true'">
            <el-form-item
               style="width:90%"
               label="钉钉Token"
               prop="dingdingAccessToken">
              <el-input placeholder="如: 52597c9b583090fd397493626c035064f03aaf92669f032d215fde67e43a807e" v-model.trim="addForm.dingdingAccessToken" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-show="addForm.isDingDingNotify.toString()==='true'" label="提醒策略">
                <el-checkbox
                    v-model="addForm.dingdingNotifyStrategy.success"
                    label="测试全通过时提醒">
                </el-checkbox>
                <el-checkbox
                    v-model="addForm.dingdingNotifyStrategy.fail"
                    label="测试存在失败时提醒">
                </el-checkbox>
            </el-form-item>
          </div>
        </transition>

        <el-form-item label="企微提醒">
            <el-radio
                v-model="addForm.isEnterpriseWechatNotify"
                :label="true">
                是
            </el-radio>
            <el-radio
                v-model="addForm.isEnterpriseWechatNotify"
                :label="false">
                否
            </el-radio>
        </el-form-item>

        <transition name="el-zoom-in-top">
          <div
              class="form-item-sub form-item-short"
              v-if="addForm.isEnterpriseWechatNotify && addForm.isEnterpriseWechatNotify.toString()==='true'">
            <el-form-item
               style="width:90%"
               label="企微Token"
               prop="enterpriseWechatAccessToken">
              <el-input placeholder="如: 618311c0-yd0f-37e0-b11d-9f7c521d8gb9" v-model.trim="addForm.enterpriseWechatAccessToken" auto-complete="off"></el-input>
            </el-form-item>

            <el-form-item v-show="addForm.isEnterpriseWechatNotify.toString()==='true'" label="提醒策略">
                <el-checkbox
                    v-model="addForm.enterpriseWechatNotifyStrategy.success"
                    label="测试全通过时提醒">
                </el-checkbox>
                <el-checkbox
                    v-model="addForm.enterpriseWechatNotifyStrategy.fail"
                    label="测试存在失败时提醒">
                </el-checkbox>
            </el-form-item>
          </div>
        </transition>

        <el-form-item label="告警邮箱" prop="alarmMailList">
          <el-select clearable style="width: 60%;" v-model="addForm['alarmMailList']" @visible-change="checkActiveMailList" multiple placeholder="请选择告警报告接受者(可多选)">
            <el-option v-for="(item,index) in alarmMailList" :key="index" :label="item.name" :value="item.mailAddress"></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="任务描述" prop='description'>
          <el-input type="textarea" :rows="4" v-model.trim="addForm.description"></el-input>
        </el-form-item>

      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="addFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="addTask" :loading="addLoading">提交</el-button>
      </div>
    </el-dialog>

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

  </section>
</template>

<script>
  import {getCaseSuiteList} from '../../../../api/caseSuite';
  import {getHosts} from "../../../../api/host";
  import {getMails} from '../../../../api/mail';
  import {getCrons, addCron, updateCron, pauseCron, resumeCron, delCron} from "../../../../api/cron";
  import {getCookie} from "@/utils/cookie";
  export default {
    data() {
      let checkTriggerInterval = (rule, value, callback) => {
        if (value !== "" && value !== null && value !== undefined){
          if (value >= 60){
            callback()
          } else{
            callback(new Error('请输入大于或等于一分钟的触发间隔！'))
            this.$message.warning({
              message: '请输入大于或等于一分钟的触发间隔！',
              center: true,
            });
          }
        }else{
          callback()
        }
      };
      return {
        Case: [],
        alarmMailList: [],
        TriggerTypes: [{name: '触发间隔', value: 'interval'},
                      {name: '具体日期', value: 'date'}],
        size: 10,
        skip: 0,
        sortBy: 'createAt',
        order: 'descending',
        pageNum: 1,
        totalNum: 0,
        sels: [],//列表选中列
        delLoading: false,
        disDel: true,
        TestStatus: false,
        listLoading: false,
        statusChangeLoading: false,
        crons:[],
        Host: [],
        editFormVisible: false,//编辑界面是否显示
        editLoading: false,
        editFormRules: {
          name: [
            { required: true, message: '请输入名称', trigger: 'blur' },
            { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
          ],
          testCaseSuiteIdList: [
            { required: true, message: '请选择测试用例组', trigger: 'blur' }
          ],
          testDomain: [
            { required: true, message: '请选择测试环境', trigger: 'blur' }
          ],
          alarmMailList: [
            { required: false, message: '请选择告警邮箱', trigger: 'blur' }
          ],
          isDingDingNotify: [
            { required: false, message: '请选择是否使用钉钉提醒', trigger: 'blur' }
          ],
          dingdingAccessToken: [
            { required: false, message: '请输入钉钉AccessToken', trigger: 'blur' }
          ],
          triggerType: [
            { required: true, message: '请选择触发类型', trigger: 'blur' }
          ],
          interval: [
            { required: false, message: '请输入触发间隔', trigger: 'blur' },
            { validator: checkTriggerInterval, trigger: 'blur' }
          ],
          runDate: [
            { required: false, message: '请输入触发时间', trigger: 'blur' }
          ],
          description: [
            { required: false, message: '请输入版本号', trigger: 'blur' },
            { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
          ]
        },
        //编辑界面数据
        editForm: {
          name: '',
          testCaseSuiteIdList: [],
          isExecuteForbiddenedCase: false,
          testDomain: '',
          alarmMailList: [],
          isDingDingNotify: false,
          dingdingNotifyStrategy: {success: false, fail: true},
          dingdingAccessToken: '',
          isEnterpriseWechatNotify: false,
          enterpriseWechatNotifyStrategy: {success: false, fail: true},
          enterpriseWechatAccessToken: '',
          triggerType: '',
          interval: 0,
          runDate: '',
          description: ''
        },
        addFormVisible: false,//新增界面是否显示
        addLoading: false,
        addFormRules: {
          name: [
            { required: true, message: '请输入名称', trigger: 'blur' },
            { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
          ],
          testCaseSuiteIdList: [
            { required: true, message: '请选择测试用例组', trigger: 'blur' }
          ],
          testDomain: [
            { required: true, message: '请选择测试环境', trigger: 'blur' }
          ],
          alarmMailList: [
            { required: false, message: '请选择告警邮箱', trigger: 'blur' }
          ],
          isDingDingNotify: [
            { required: false, message: '请选择是否使用钉钉提醒', trigger: 'blur' }
          ],
          dingdingAccessToken: [
            { required: false, message: '请输入钉钉AccessToken', trigger: 'blur' }
          ],
          triggerType: [
            { required: true, message: '请选择触发类型', trigger: 'blur' }
          ],
          interval: [
            { required: false, message: '请输入触发间隔', trigger: 'blur' },
            { validator: checkTriggerInterval, trigger: 'blur' }
          ],
          runDate: [
            { required: false, message: '请输入触发时间', trigger: 'blur' }
          ],
          description: [
            { required: false, message: '请输入版本号', trigger: 'blur' },
            { max: 1024, message: '不能超过1024个字符', trigger: 'blur' }
          ]
        },
        //新增界面数据
        addForm: {
          name: '',
          testCaseSuiteIdList: [],
          isExecuteForbiddenedCase: false,
          testDomain: '',
          alarmMailList: [],
          isDingDingNotify: false,
          dingdingNotifyStrategy: {success: false, fail: true},
          dingdingAccessToken: '',
          isEnterpriseWechatNotify: false,
          enterpriseWechatNotifyStrategy: {success: false, fail: true},
          enterpriseWechatAccessToken: '',
          triggerType: '',
          interval: '',
          runDate: '',
          description: ''
        },
        filters: {
          name: ''
        },
        pickerOptions: {
          disabledDate: (time) => {
             return time.getTime() < (Date.now() - 8.64e7)
          }
        }
      }
    },
    methods: {
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
        })
      },
      getTask(){
        let self = this;
        self.listLoading = true;
        let header = {};
        let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
          projectId: self.$route.params.project_id};
        if (self.filters.name.trim() !== ''){
          params['name'] = self.filters.name.trim()
        };
        getCrons(params, header).then((res) => {
          self.listLoading = false;
          let{status, data} = res;
          if (status === 'ok'){
            self.totalNum = data.totalNum;
            self.crons = data.rows;
          }
          else {
            self.$message.error({
              message: data,
              center: true,
            })
          }
        }).catch((error) => {
          self.$message.error({
              message: '定时任务列表获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      getMail(){
        let self = this;
        let header = {};
        let params = {status: true, projectId: self.$route.params.project_id};
        self.listLoading = true;
        getMails(self.$route.params.project_id, params, header).then((res) => {
          self.listLoading = false;
          let{status, data} = res;
          if (status === 'ok'){
            self.alarmMailList = data.rows
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
        })
      },
      handleSizeChange(val){
        let self = this;
        self.size = val;
        self.listLoading = true;
        let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
          projectId: self.$route.params.project_id};
        let header = {};
        getCrons(params, header).then((res) => {
          self.listLoading = false;
          let{status, data} = res;
          if (status === 'ok'){
            self.totalNum = data.totalNum;
            self.crons = data.rows;
          }
          else {
            self.$message.error({
              message: data,
              center: true,
            })
          }
        }).catch((error) => {
          self.$message.error({
              message: '定时任务列表获取失败，请稍后刷新重试哦~',
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
        getCrons(params, header).then((res) => {
          self.listLoading = false;
          let{status, data} = res;
          if (status === 'ok'){
            self.totalNum = data.totalNum;
            self.crons = data.rows;
          }
          else {
            self.$message.error({
              message: data,
              center: true,
            })
          }
        }).catch((error) => {
          self.$message.error({
              message: '定时任务列表获取失败，请稍后刷新重试哦~',
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
        let params = {size: self.size, skip: self.skip, sortBy: self.sortBy, order: self.order,
          projectId: self.$route.params.project_id};
        let header = {};
        getCrons(params, header).then((res) => {
          self.listLoading = false;
          let{status, data} = res;
          if (status === 'ok'){
            self.totalNum = data.totalNum;
            self.crons = data.rows;
          }
          else {
            self.$message.error({
              message: data,
              center: true,
            })
          }
        }).catch((error) => {
          self.$message.error({
              message: '定时任务列表获取失败，请稍后刷新重试哦~',
              center: true,
          });
          self.listLoading = false;
        })
      },
      addTask(){
        this.$refs.addForm.validate((valid) => {
          let self = this;
          if (valid) {
            if (!(self.addForm.runDate && self.addForm.runDate.toString().trim() !== '') && !(self.addForm.interval &&
                self.addForm.interval.toString().trim() !== '')){
                if (self.addForm.triggerType === 'interval')
                  self.$message.warning({
                        message: '请输入触发间隔',
                        center: true,
                      })
                else if (self.addForm.triggerType === 'date'){
                  self.$message.warning({
                      message: '请输入具体日期',
                      center: true,
                    })
                }
            }else if (self.addForm.triggerType === 'date' && self.addForm.runDate < Date.now()){
              self.$message.warning({
                message: '人生不能重来哦~请输入「此刻」以后的日期',
                center: true,
              })
            }
            else{
                this.$confirm('确认提交吗？', '提示', {}).then(() => {
                let self = this;
                self.addLoading = true;
                let params ={
                  name: self.addForm.name,
                  testCaseSuiteIdList: self.addForm.testCaseSuiteIdList,
                  testDomain: self.addForm.testDomain,
                  isExecuteForbiddenedCase: self.addForm.isExecuteForbiddenedCase,
                  triggerType: self.addForm.triggerType,
                  description: self.addForm.description,
                  alarmMailList: self.addForm.alarmMailList,
                  isDingDingNotify: self.addForm.isDingDingNotify,
                  dingdingAccessToken: self.addForm.dingdingAccessToken,
                  dingdingNotifyStrategy: self.addForm.dingdingNotifyStrategy,
                  isEnterpriseWechatNotify: self.addForm.isEnterpriseWechatNotify,
                  enterpriseWechatAccessToken: self.addForm.enterpriseWechatAccessToken,
                  enterpriseWechatNotifyStrategy: self.addForm.enterpriseWechatNotifyStrategy,
                  creatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户',
                  lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                };
                if (self.addForm.runDate && self.addForm.runDate.toString().trim() !== ''){
                  params['runDate'] = self.addForm.runDate
                }
                if (self.addForm.interval && self.addForm.interval.toString().trim() !== ''){
                  params['interval'] = Number(self.addForm.interval)
                }
                let header = {};
                addCron(self.$route.params.project_id, params, header).then((res) => {
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
                    self.getTask()
                  }
                  else {
                    self.addFormVisible = false
                    self.$message.error({
                      message: data,
                      center: true,
                    })
                    self.$refs['addForm'].resetFields();
                    self.addFormVisible = false;
                    self.getTask()
                  }
                });
              });
            }
          }
        });
      },
      editTask(){
        this.$refs.editForm.validate((valid) => {
          if (valid) {
            let self = this;
            if (!(self.editForm.runDate && self.editForm.runDate.toString().trim() !== '') && !(self.editForm.interval &&
                self.editForm.interval.toString().trim() !== '')){
                if (self.editForm.triggerType === 'interval')
                  self.$message.warning({
                        message: '请输入触发间隔',
                        center: true,
                      });
                else if (self.editForm.triggerType === 'date'){
                  self.$message.warning({
                      message: '请输入具体日期',
                      center: true,
                    })
                }
            }else if (self.editForm.triggerType === 'date' && self.editForm.runDate < Date.now()){
              self.$message.warning({
                message: '人生不能重来哦~请输入「此刻」以后的日期',
                center: true,
              })
            }else{
              let self = this;
              this.$confirm('确认提交吗？', '提示', {}).then(() => {
                self.editLoading = true;
                let params ={
                  name: self.editForm.name,
                  testCaseSuiteIdList: self.editForm.testCaseSuiteIdList,
                  isExecuteForbiddenedCase: self.editForm.isExecuteForbiddenedCase,
                  testDomain: self.editForm.testDomain,
                  triggerType: self.editForm.triggerType,
                  next_run_time: self.editForm.next_run_time, // 用于判断是否要resume定时任务
                  description: self.editForm.description,
                  alarmMailList: self.editForm.alarmMailList,
                  isDingDingNotify: self.editForm.isDingDingNotify || false,
                  dingdingAccessToken: self.editForm.dingdingAccessToken || '',
                  dingdingNotifyStrategy: self.editForm.dingdingNotifyStrategy,
                  isEnterpriseWechatNotify: self.editForm.isEnterpriseWechatNotify || false,
                  enterpriseWechatAccessToken: self.editForm.enterpriseWechatAccessToken || '',
                  enterpriseWechatNotifyStrategy: self.editForm.enterpriseWechatNotifyStrategy,
                  lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                };
                if (self.editForm.runDate && self.editForm.runDate.toString().trim() !== ''){
                  params['runDate'] = self.editForm.runDate
                }
                if (self.editForm.interval && self.editForm.interval.toString().trim() !== ''){
                  params['interval'] = Number(self.editForm.interval)
                }
                let header = {};
                updateCron(self.editForm._id, params, header).then((res) => {
                  self.editLoading = false;
                  let { status, data } = res;
                  if (status === 'ok') {
                    self.editFormVisible = false
                    self.$message.success({
                      message: '编辑成功',
                      center: true,
                    });
                    self.editFormVisible = false;
                    self.getTask()
                  }
                  else {
                    self.editFormVisible = false
                    self.$message.error({
                      message: data,
                      center: true,
                    })
                    self.editFormVisible = false;
                    self.getTask()
                  }
                });
              });
            }
          }
        });
      },
      handleChangeStatus(index, row){
        let self = this;
        self.statusChangeLoading = true;
        let header = {};
        let params = {};
        if (row.status !== 'PAUSED'){
          pauseCron(row._id, params, header).then((res) => {
            self.statusChangeLoading = false;
            let { status, data } = res;
            if (status === 'ok') {
              self.$message.success({
                message: data,
                center: true,
              });
            }else{
              self.$message.error({
                message: data,
                center: true,
              });
            }
            self.getTask()
          }).catch((error) => {
            self.$message.error({
                message: '定时任务状态变更失败，请稍后刷新重试哦~',
                center: true,
            });
            self.statusChangeLoading = false;
          })
        }else {
          resumeCron(row._id, params, header).then((res) => {
            self.statusChangeLoading = false;
            let { status, data } = res;
            if (status === 'ok') {
              self.$message.success({
                message: data,
                center: true,
              });
            }else {
              self.$message.error({
                message: data,
                center: true,
              });
            }
            self.getTask()
          }).catch((error) => {
            self.$message.error({
                message: '定时任务状态变更失败，请稍后刷新重试哦~',
                center: true,
            });
            self.statusChangeLoading = false;
            self.getTask()
          })
        }
      },
      // 获取用例列表
      getCaseSuites() {
        this.listLoading = true;
        let self = this;
        let hearder = {};
        let params = {status: true, projectId: self.$route.params.project_id};
        getCaseSuiteList(self.$route.params.project_id, params, hearder).then((res) => {
          self.listLoading = false;
          let { status, data } = res;
          if (status === 'ok') {
            self.Case = data.rows
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
        }).then(() => {
          this.listLoading = true;
          let self = this;
          let header = {};
          let params = {}
          delCron(row._id, params, header).then((res) =>{
            let { status, data } = res;
            if (status === 'ok') {
              self.$message.success({
                message: data,
                center: true,
              });
            }else {
              self.$message.error({
                message: data,
                center: true,
              });
            }
            self.getTask()
          });

        }).catch(() => {
        });

      },
      selsChange: function (sels) {
        if (sels.length>0) {
          this.sels = sels;
          this.update = false
        } else {
          this.update = true
        }
      },
      //批量删除
      batchRemove: function () {
        let ids = this.sels.map(item => item.id);
        let self = this;
        this.$confirm('确认删除选中记录吗？', '提示', {
          type: 'warning'
        }).then(() => {
          self.listLoading = true;
          $.ajax({
            type: "post",
            url: test+"/api/automation/del_case",
            async: true,
            data:JSON.stringify({ project_id: Number(this.$route.params.project_id), ids: ids}),
            headers: {
              "Content-Type": "application/json",
              Authorization: 'Token '+JSON.parse(sessionStorage.getItem('token'))
            },
            timeout: 5000,
            success: function(data) {
              self.listLoading = false;
              if (data.code === '999999') {
                self.$message({
                  message: '删除成功',
                  center: true,
                  type: 'success'
                })
              }
              else {
                self.$message.error({
                  message: data.msg,
                  center: true,
                })
              }
              self.getCaseSuiteList();
            },
          })
        }).catch(() => {

        });
      },
      // TODO 抽出成通用方法
      stringToDate : function(dateStr,separator){
         if(!separator){
                separator="-";
         }
         var dateArr = dateStr.toString().split(separator);
         var year = parseInt(dateArr[0]);
         var month;
         //处理月份为04这样的情况
         if(dateArr[1].indexOf("0") == 0){
             month = parseInt(dateArr[1].substring(1));
         }else{
              month = parseInt(dateArr[1]);
         }
         var day = parseInt(dateArr[2]);
         var date = new Date(year,month -1,day);
         return date;
     },
      //显示编辑界面
      handleEdit: function (index, row) {
        this.editFormVisible = true;
        if (row['runDate'] && row['runDate'].constructor === String){
          row['runDate'] = this.stringToDate(row['runDate'])
        }
        this.editForm = Object.assign({}, this.editForm, row); // 新字段上线，需要使用this.editForm添加
      },
      //显示新增界面
      handleAdd: function () {
        this.addFormVisible = true;
      },
      editFormTriggerTypeChange(selVal){
        if (selVal === 'interval'){
          this.editForm.runDate = ''
        }else if (selVal === 'date'){
          this.editForm.interval = ''
        }
      },
      addFormTriggerTypeChange(selVal){
        if (selVal === 'interval'){
          this.addForm.runDate = ''
        }else if (selVal === 'date'){
          this.addForm.interval = ''
        }
      },
      checkActiveCaseSuite: function(){
        let self = this;
        if (self.Case.length < 1){
          self.$message.warning({
              message: '未找到「启用的测试用例组」哦, 请前往「自动化测试」进行设置',
              center: true,
          })
        }
      },
      checkActiveMailList: function(){
        let self = this;
        if (self.alarmMailList.length < 1){
          self.$message.warning({
              message: '未找到启用的「告警邮箱」哦, 请前往「邮箱配置」进行设置',
              center: true,
          })
        }
      },
      checkActiveEnv: function(){
        let self = this;
        if (self.Host.length < 1){
          self.$message.warning({
              message: '未找到启用的「测试环境」哦, 请前往「Host配置」进行设置',
              center: true,
          })
        }
      },
      // 修改table tr行的背景色
      reportRowStyle({ row, rowIndex }){
        if (row.status === 'PAUSED')
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
      this.getMail();
      this.getTask();
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
    .sub-form-item{
      padding-left: 40px;
    }
    .form-item-sub{
      position: relative;
      background-color: #f5f7fa;
      padding: 10px 0;
      margin-bottom: 10px;
      border-radius: 4px;
      box-shadow: inset 0 0 3px 0px #7c7c7c61;
    }
    .form-item-sub::before{
      position: absolute;
      content: '';
      display: block;
      width: 0;
      height: 0;
      top: -8px;
      left: 220px;
      border-bottom: 8px solid #ecedef;
      border-left: 8px solid transparent;
      border-right: 8px solid transparent;
      border-top: 0px solid transparent;
    }
    .form-item-short>>>.el-form-item__content{
      margin-left: 100px !important;
    }
    .form-item-short>>>.el-input{
      margin: 0 10px;
    }
    .el-form-item:last-child{
      margin-bottom: 0;
    }
    ::-webkit-scrollbar {
        display: none;
    }
</style>
