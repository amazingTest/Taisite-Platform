<template>
    <section>
        <div class="toolbar">
            <router-link :to="{ name: '用例接口列表', params: {
                    project_id: this.$route.params.project_id,
                    case_id: this.$route.params.case_id,
                  }}" style='text-decoration: none;color: aliceblue;'>
                <el-button class="return-list"><i class="el-icon-d-arrow-left" style="margin-right: 5px"></i>返回列表</el-button>
            </router-link>
            <router-link :to="{ name: '用例接口列表', params: {
                    project_id: this.$route.params.project_id,
                    case_id: this.$route.params.case_id,
                  }}" style='text-decoration: none;color: aliceblue;'>
                <el-button round class="el-icon-close" style="float: right; margin-right: 35px"> 取消</el-button>
            </router-link>
            <el-button class="return-list el-icon-check" type="primary" style="float: right; margin-right: 15px" @click.native="updateApi"> 保存</el-button>
        </div>
        <el-form :model="form" ref="form" :rules="FormRules">
            <div style="border: 1px solid #e6e6e6;margin-bottom: 10px;padding:15px">
                <el-form-item label="接口名称:" label-width="83px" prop="name">
                    <el-input v-model.trim="form.name" placeholder="名称" auto-complete></el-input>
                </el-form-item>
                <el-row :gutter="10">
                    <el-col :span="4">
                        <el-form-item label="URL:" label-width="83px">
                            <el-select v-model="form.request4"  placeholder="请求方式" @change="checkRequest">
                                <el-option v-for="(item,index) in request" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span="2">
                        <el-form-item>
                            <el-select v-model="form.Http4" placeholder="HTTP协议">
                                <el-option v-for="(item,index) in Http" :key="index+''" :label="item.label" :value="item.value"></el-option>
                            </el-select>
                        </el-form-item>
                    </el-col>
                    <el-col :span='10'>
                      <el-form-item prop="domain">
                        <el-input v-model.trim="form.domain" placeholder="请输入访问域名(优先级最高)" auto-complete></el-input>
                      </el-form-item>
                    </el-col>
                    <el-col :span='5'>
                        <el-form-item prop="addr">
                            <el-input v-model.trim="form.addr" placeholder="请输入接口路由" auto-complete></el-input>
                        </el-form-item>
                    </el-col>
                    <el-col :span='3' style="float: right">
                        <el-checkbox label='请求前是否清除Cookie' v-model.trim="form.isClearCookie">
                        </el-checkbox>
                    </el-col>
                </el-row>
                <el-row :gutter="10">
                  <el-form-item prop="description">
                    <el-input type="textarea" v-model.trim="form.description" placeholder="请输入用例描述" auto-complete></el-input>
                  </el-form-item>
                </el-row>
            </div>
            <el-row :span="24">
                <el-collapse v-model="activeNames" @change="handleChange">
                    <el-collapse-item title="请求头部" name="1">
                        <el-table :data="form.head" highlight-current-row>
                            <el-table-column prop="name" label="标签" min-width="28%" sortable>
                                <template slot-scope="scope">
                                    <el-select placeholder="请输入/选择标签"
                                       clearable
                                       filterable
                                       allow-create
                                       default-first-option
                                       v-model.trim="scope.row.name"
                                       style="width: 90%">
                                          <el-option v-for="(item,index) in header" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                    </el-select>
                                </template>
                            </el-table-column>
                            <el-table-column prop="value" label="内容" min-width="40%" sortable>
                                <template slot-scope="scope">
                                    <el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入内容"></el-input>
                                </template>
                            </el-table-column>

                            <el-table-column label="操作" min-width="7%">
                                <template slot-scope="scope">
                                    <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delHead(scope.$index)"></i>
                                </template>
                            </el-table-column>
                            <el-table-column label="" min-width="5%">
                                <template slot-scope="scope">
                                    <el-button v-if="scope.$index===(form.head.length-1)" size="mini" class="el-icon-plus" @click="addHead"></el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </el-collapse-item>
                    <el-collapse-item title="请求参数" name="2">
                        <div style="margin: 5px">
                            <el-row :span="24">
                                <!--<el-col :span="4"><el-radio v-model="radio" label="form-data">表单(form-data)</el-radio></el-col>-->
                                <el-col v-if="request3" :span="4"><el-radio v-model="radio"  label="raw">源数据(raw)</el-radio></el-col>
                                <!--<el-col v-if="request3" :span="16"><el-checkbox v-model="radioType" label="3" v-show="ParameterType">表单转源数据</el-checkbox></el-col>-->
                            </el-row>
                        </div>
                        <!--<el-table :data="form.parameter" highlight-current-row :class="ParameterType? 'parameter-a': 'parameter-b'">-->
                            <!--<el-table-column prop="name" label="参数名" min-width="28%" sortable>-->
                                <!--<template slot-scope="scope">-->
                                    <!--<el-input v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入参数值"></el-input>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                            <!--<el-table-column prop="value" label="参数值" min-width="40%" sortable>-->
                                <!--<template slot-scope="scope">-->
                                    <!--<el-input v-model.trim="scope.row.value" :value="scope.row.value" placeholder="请输入参数值"></el-input>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                            <!--<el-table-column prop="interrelate" label="是否关联" min-width="13%" sortable>-->
                                <!--<template slot-scope="scope">-->
                                    <!--<el-switch v-model="scope.row.interrelate">-->
                                    <!--</el-switch>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                            <!--<el-table-column min-width="7%">-->
                                <!--<template slot-scope="scope">-->
                                    <!--<el-button type="primary" size="mini" style="margin-bottom: 5px" v-show="scope.row.interrelate" @click="handleCorrelation(scope.$index, scope.row)">关联</el-button>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                            <!--<el-table-column label="操作" min-width="7%">-->
                                <!--<template slot-scope="scope">-->
                                    <!--<i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delParameter(scope.$index)"></i>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                            <!--<el-table-column label="" min-width="5%">-->
                                <!--<template slot-scope="scope">-->
                                    <!--<el-button v-if="scope.$index===(form.parameter.length-1)" size="mini" class="el-icon-plus" @click="addParameter"></el-button>-->
                                <!--</template>-->
                            <!--</el-table-column>-->
                        <!--</el-table>-->
                        <template>
                            <el-form-item label="" prop="parameterRaw">
                              <el-input type="textarea" :rows="5" placeholder="请输入参数内容({'username': 'test'})" v-model.trim="form.parameterRaw"></el-input>
                            </el-form-item>
                        </template>
                    </el-collapse-item>


                    <el-collapse-item title="返回结果设置全局变量" name="3">
                      <el-table :data="form.setGlobalVars" highlight-current-row>
                        <el-table-column prop="name" label="变量名" min-width="28%">
                          <template slot-scope="scope">
                            <el-input  v-model.trim="scope.row.name" :value="scope.row.name" placeholder="请输入变量名"></el-input>
                          </template>
                        </el-table-column>
                        <el-table-column prop="query" label="变量查询语句" min-width="40%" sortable>
                          <template slot-scope="scope">
                            <el-select
                              style="width: 60%;"
                              v-model.trim="scope.row.query"
                              @change="addSuffix(scope.row.query)"
                              multiple
                              clearable
                              filterable
                              default-first-option
                              allow-create
                              placeholder="请输入变量查询语句(不输入则返回整个JSON字符串)">
                            </el-select>
                          </template>
                        </el-table-column>
                        <el-table-column label="操作" min-width="7%">
                          <template slot-scope="scope">
                            <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delGlobalVars(scope.$index)"></i>
                          </template>
                        </el-table-column>
                        <el-table-column label="" min-width="5%">
                          <template slot-scope="scope">
                            <el-button v-if="scope.$index===(form.setGlobalVars.length-1)" size="mini" class="el-icon-plus" @click="addGlobalVars"></el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-collapse-item>

                    <el-collapse-item title="测试结果校验" name="3">
                        <el-card class="box-card">
                            <div slot="header" class="clearfix">
                                <el-radio-group v-model="form.check">
                                    <el-radio-button label="noCheck"><div>不校验</div></el-radio-button>
                                    <el-radio-button label="checkHttpStatusCode"><div>HTTP状态校验</div></el-radio-button>
                                    <el-radio-button label="checkJsonRegex"><div>JSON正则校验</div></el-radio-button>
                                    <el-radio-button label="checkNumber"><div>数值校验</div></el-radio-button>
                                    <el-radio-button label="checkSimilarity"><div>智能相似度校验</div></el-radio-button>
                                </el-radio-group>
                            </div>

                            <div v-show="showHttpCodeCheck">
                                <el-select v-model="form.checkHttp" clearable placeholder="HTTP状态">
                                    <el-option v-for="(item,index) in httpCode" :key="index+''" :label="item.label" :value="item.value"></el-option>
                                </el-select>
                            </div>
                            <div v-show="showJsonRegexCheck">
                                <el-collapse-item title="JSON正则校验" name="4">
                                  <el-table :data="form.checkRegex" highlight-current-row>
                                    <el-table-column prop="regex" label="正则语句" min-width="28%">
                                      <template slot-scope="scope">
                                        <el-input  v-model.trim="scope.row.regex" placeholder="请输入正则语句"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column prop="query" label="变量查询语句" min-width="40%">
                                      <template slot-scope="scope">
                                        <el-select
                                          style="width: 60%;"
                                          v-model.trim="scope.row.query"
                                          @change="addSuffix(scope.row.query)"
                                          multiple
                                          filterable
                                          clearable
                                          default-first-option
                                          allow-create
                                          placeholder="请输入变量查询语句(不输入则返回整个JSON字符串)">
                                        </el-select>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="操作" min-width="7%">
                                      <template slot-scope="scope">
                                        <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delCheckRegex(scope.$index)"></i>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="" min-width="5%">
                                      <template slot-scope="scope">
                                        <el-button v-if="scope.$index===(form.checkRegex.length-1)" size="mini" class="el-icon-plus" @click="addCheckRegex"></el-button>
                                      </template>
                                    </el-table-column>
                                  </el-table>
                                </el-collapse-item>
                            </div>
                            <div v-show="showNumberCheck">
                                <el-collapse-item title="数值校验" name="5">
                                  <el-table :data="form.checkNumber" highlight-current-row>
                                    <el-table-column label="数值一" min-width="3%">
                                      <template slot-scope="scope">
                                        <el-input v-model.trim="scope.row.expressions.firstArg" placeholder="请输入数值一"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="运算" min-width="3%">
                                      <template slot-scope="scope">
                                        <el-select  v-model.trim="scope.row.expressions.operator" clearable placeholder="请选择运算">
                                          <el-option v-for="(item,index) in operator" :key="index" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="数值二" min-width="3%">
                                      <template slot-scope="scope">
                                        <el-input v-model.trim="scope.row.expressions.secondArg" placeholder="请输入数值二"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="判断" min-width="3%">
                                      <template slot-scope="scope">
                                        <el-select  v-model.trim="scope.row.expressions.judgeCharacter" clearable placeholder="请选择判断">
                                          <el-option v-for="(item,index) in judgeCharacter" :key="index" :label="item.label" :value="item.value"></el-option>
                                        </el-select>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="期待结果" min-width="3%">
                                      <template slot-scope="scope">
                                        <el-input v-model.trim="scope.row.expressions.expectResult" placeholder="请输入期待结果"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="操作" min-width="1%">
                                      <template slot-scope="scope">
                                        <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delCheckNumber(scope.$index)"></i>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="" min-width="5%">
                                      <template slot-scope="scope">
                                        <el-button v-if="scope.$index===(form.checkNumber.length-1)" size="mini" class="el-icon-plus" @click="addCheckNumber"></el-button>
                                      </template>
                                    </el-table-column>
                                  </el-table>
                                </el-collapse-item>
                            </div>

                            <div v-show="showSimilarityCheck">
                                <el-collapse-item title="智能相似度校验" name="6">
                                  <el-table :data="form.checkSimilarity" highlight-current-row>
                                    <el-table-column label="文本一" min-width="28%">
                                      <template slot-scope="scope">
                                        <el-input  v-model.trim="scope.row.baseText" placeholder="请输入文本一"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="文本二" min-width="28%">
                                      <template slot-scope="scope">
                                        <el-input  v-model.trim="scope.row.compairedText" placeholder="请输入文本二"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="目标相似度" min-width="28%">
                                      <template slot-scope="scope">
                                        <el-input type="number" v-model.trim="scope.row.targetSimilarity" placeholder="请输入目标相似度(0～1)"></el-input>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="操作" min-width="7%">
                                      <template slot-scope="scope">
                                        <i class="el-icon-delete" style="font-size:30px;cursor:pointer;" @click="delCheckSimilarity(scope.$index)"></i>
                                      </template>
                                    </el-table-column>
                                    <el-table-column label="" min-width="5%">
                                      <template slot-scope="scope">
                                        <el-button v-if="scope.$index===(form.checkSimilarity.length-1)" size="mini" class="el-icon-plus" @click="addCheckSimilarity"></el-button>
                                      </template>
                                    </el-table-column>
                                  </el-table>
                                </el-collapse-item>
                            </div>

                        </el-card>
                    </el-collapse-item>
                </el-collapse>
            </el-row>
        </el-form>
    </section>
</template>
<script>
    import {getCaseDetail, updateCase} from '../../../../api/testCase';
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
            return {
                request: [{ label: "GET", value: "GET"},
                         { label: "POST", value: "POST"},
                         { label: "PUT", value: "PUT"},
                         { label: "DELETE", value: "DELETE"},
                         { label: "OPTIONS", value: "OPTIONS"},
                         { label: "PATCH", value: "PATCH"},
                         { label: "HEAD", value: "HEAD"}],
                Http: [{value: 'HTTP', label: 'HTTP'},
                    {value: 'HTTPS', label: 'HTTPS'}],
                ParameterType: true,
                radio: "raw",
                header: [{value: 'Accept', label: 'Accept'},
                    {value: 'Accept-Charset', label: 'Accept-Charset'},
                    {value: 'Accept-Encoding', label: 'Accept-Encoding'},
                    {value: 'Accept-Language', label: 'Accept-Language'},
                    {value: 'Accept-Ranges', label: 'Accept-Ranges'},
                    {value: 'Authorization', label: 'Authorization'},
                    {value: 'Cache-Control', label: 'Cache-Control'},
                    {value: 'Connection', label: 'Connection'},
                    {value: 'Cookie', label: 'Cookie'},
                    {value: 'Content-Length', label: 'Content-Length'},
                    {value: 'Content-Type', label: 'Content-Type'},
                    {value: 'Content-MD5', label: 'Content-MD5'},
                    {value: 'Date', label: 'Date'},
                    {value: 'Expect', label: 'Expect'},
                    {value: 'From', label: 'From'},
                    {value: 'Host', label: 'Host'},
                    {value: 'If-Match', label: 'If-Match'},
                    {value: 'If-Modified-Since', label: 'If-Modified-Since'},
                    {value: 'If-None-Match', label: 'If-None-Match'},
                    {value: 'If-Range', label: 'If-Range'},
                    {value: 'If-Unmodified-Since', label: 'If-Unmodified-Since'},
                    {value: 'Max-Forwards', label: 'Max-Forwards'},
                    {value: 'Origin', label: 'Origin'},
                    {value: 'Pragma', label: 'Pragma'},
                    {value: 'Proxy-Authorization', label: 'Proxy-Authorization'},
                    {value: 'Range', label: 'Range'},
                    {value: 'Referer', label: 'Referer'},
                    {value: 'TE', label: 'TE'},
                    {value: 'Upgrade', label: 'Upgrade'},
                    {value: 'User-Agent', label: 'User-Agent'},
                    {value: 'Via', label: 'Via'},
                    {value: 'Warning', label: 'Warning'}],
                headers: [],
                httpCode:[{value: '200', label: '200'},
                    {value: '302', label: '302'},
                    {value: '400', label: '400'},
                    {value: '401', label: '401'},
                    {value: '404', label: '404'},
                    {value: '500', label: '500'},
                    {value: '502', label: '502'},
                    {value: '504', label: '504'}],
                operator:[{value: '+', label: '加上'},
                    {value: '-', label: '减去'},
                    {value: '*', label: '乘以'},
                    {value: '/', label: '除以'}],
                judgeCharacter:[{value: '<', label: '小于'},
                    {value: '<=', label: '小于等于'},
                    {value: '>', label: '大于'},
                    {value: '>=', label: '大于等于'},
                    {value: '==', label: '等于'}],
                radioType: "",
                result: true,
                activeNames: ['1', '2', '3', '4', '5', '6'],
                id: "",
                ApiList: [],
                ApiResponse: [],
                apiResponseLoading: false,
                saveCorrelation: false,
                showHttpCodeCheck: false,
                showJsonRegexCheck: false,
                showNumberCheck: false,
                showSimilarityCheck: false,
                sels: [],//列表选中列
                request3:true,
                form: {
                    name: '',
                    request4: 'GET',
                    Http4: 'HTTP',
                    addr: '',
                    domain: '',
                    description: '',
                    isClearCookie: false,
                    setGlobalVars: [{name: "", query: []}],
                    checkRegex: [{regex: "", query: []}],
                    checkNumber: [{expressions:{'firstArg': '', 'operator': '', 'secondArg': '', 'judgeCharacter': '', 'expectResult': ''}}],
                    checkSimilarity: [{'baseText': '', 'compairedText': '', 'targetSimilarity': null}],
                    head: [{name: "", value: ""}],
                    parameterRaw: "",
                    parameter: [{name: "", value: ""},
                        {name: "", value: ""}],
                    parameterType: "",
                    check: "checkSimilarity",
                    RegularParam: "",
                    checkHttp: "",
                },
                FormRules: {
                    name : [{ required: true, message: '请输入名称', trigger: 'blur' }],
                    addr : [{ required: true, message: '请输入接口路由', trigger: 'blur' },
                            { validator: checkRoute, trigger: 'blur' }],
                    parameterRaw: [{ required: false, message: '请输入名称', trigger: 'blur' },
                      { validator: checkJson, trigger: 'blur' }],
                    checkRegex: [{ required: false, message: '请输入名称', trigger: 'blur' }]
                }
            }
        },
        methods: {
            checkRequest(){
                let request = this.form.request4;
                if (request==="GET" || request==="DELETE"){
                    this.request3=false
                } else {
                    this.request3=true
                }
            },
            handleCurrentChange(val) {
                this.currentRow = val;
            },
            selsChange(sels){
                this.sels = sels;
            },
            handleResponse(index) {
                this.ApiResponse = [];
                this.ApiList[index].response.forEach((item) =>{
                    this.ApiResponse.push(item)
                })
            },
            updateApi: function () {
                this.$refs.form.validate((valid) => {
                    if (valid) {
                        let self = this;
                        this.$confirm('确认提交吗？', '提示', {}).then(() => {
                            // 删除后缀
                            self.form.setGlobalVars.forEach((setGlobalVar) => {
                              setGlobalVar.query.forEach((query, index) => {
                                setGlobalVar.query[index] = query.replace(/\([0-9]+\)/, "");
                              })
                            });
                            self.form.checkRegex.forEach((checkRegex) => {
                              checkRegex.query.forEach((query, index) => {
                                checkRegex.query[index] = query.replace(/\([0-9]+\)/, "");
                              })
                            });
                            let params = {
                                name: self.form.name,
                                requestProtocol: self.form.Http4,
                                requestMethod: self.form.request4,
                                route: self.form.addr,
                                domain: self.form.domain,
                                description : self.form.description,
                                headers: self.form.head,
                                isClearCookie: self.form.isClearCookie,
                                setGlobalVars: self.form.setGlobalVars,
                                checkResponseData: self.form.checkRegex,
                                checkResponseNumber: self.form.checkNumber,
                                checkResponseSimilarity: self.form.checkSimilarity,
                                presendParams: self.form.parameterRaw,
                                lastUpdatorNickName: unescape(getCookie('nickName').replace(/\\u/g, '%u')) || '未知用户'
                            };

                            if (self.form.checkHttp){
                              params["checkHttpCode"] = self.form.checkHttp
                            }
                            if (self.form.check === 'noCheck'){
                              params["checkHttpCode"] = null
                              params["checkResponseData"] = null
                              params["checkResponseNumber"] = null
                              params["checkResponseSimilarity"] = null
                            }
                            let header = {};
                            updateCase(self.$route.params.project_id, self.$route.params.case_suite_id, self.$route.params.case_id,
                              params, header).then((res) => {
                                let {status, data} = res;
                                if (status === 'ok'){
                                  self.$router.push({ name: '用例接口列表', params: {
                                      project_id: self.$route.params.project_id,
                                      case_suite_id: self.$route.params.case_suite_id,
                                      }});
                                  self.$message({
                                      message: '修改成功',
                                      center: true,
                                      type: 'success'
                                  })
                                }else {
                                  self.$message.error({
                                      message: data,
                                      center: true,
                                  })
                                }
                            })
                        })
                    }
                })
            },
            addHead() {
                let headers = {name: "", value: ""};
                this.form.head.push(headers)
            },
            delHead(index) {
                this.form.head.splice(index, 1);
                if (this.form.head.length === 0) {
                    this.form.head.push({name: "", value: ""})
                }
            },
            addGlobalVars() {
              let globalVars = {name: "", query: []};
              this.form.setGlobalVars.push(globalVars)
            },
            delGlobalVars(index) {
              this.form.setGlobalVars.splice(index, 1);
              if (this.form.setGlobalVars.length === 0) {
                this.form.setGlobalVars.push({name: "", query: []})
              }
            },
            addCheckRegex() {
              let checkRegex = {regex: "", query: []};
              this.form.checkRegex.push(checkRegex)
            },
            delCheckRegex(index) {
              this.form.checkRegex.splice(index, 1);
              if (this.form.checkRegex.length === 0) {
                this.form.checkRegex.push({regex: "", query: []})
              }
            },
            addCheckNumber() {
              let checkNumber = {expressions:{'firstArg': '', 'operator': '', 'secondArg': '', 'judgeCharacter': '', 'expectResult': ''}};
              this.form.checkNumber.push(checkNumber)
            },
            delCheckNumber(index) {
              this.form.checkNumber.splice(index, 1);
              if (this.form.checkNumber.length === 0) {
                this.form.checkNumber.push({expressions:{'firstArg': '', 'operator': '', 'secondArg': '', 'judgeCharacter': '', 'expectResult': ''}})
              }
            },
            addCheckSimilarity() {
              let checkSimilarity = {'baseText': '', 'compairedText': '', 'targetSimilarity': null};
              this.form.checkSimilarity.push(checkSimilarity)
            },
            delCheckSimilarity(index) {
              this.form.checkSimilarity.splice(index, 1);
              if (this.form.checkSimilarity.length === 0) {
                this.form.checkSimilarity.push({'baseText': '', 'compairedText': '', 'targetSimilarity': null})
              }
            },
            addParameter() {
                let headers = {name: "", value: ""};
                this.form.parameter.push(headers)
            },
            delParameter(index) {
                this.form.parameter.splice(index, 1);
                if (this.form.parameter.length === 0) {
                    this.form.parameter.push({name: "", value: ""})
                }
            },
            changeParameterType() {
                if (this.radio === 'form-data') {
                    this.ParameterType = true
                } else {
                    this.ParameterType = false
                }
            },
            handleChange(val) {
            },
            getCaseApiInfo() {
                let self = this;
                let header ={};
                getCaseDetail(self.$route.params.project_id, self.$route.params.case_suite_id, self.$route.params.case_id,
                        header).then((res) => {
                          let {status, data} = res;
                          if (status === 'ok'){
                            self.form.name = data.name;
                            self.form.request4 = data.requestMethod;
                            self.form.Http4 = data.requestProtocol;
                            self.form.addr = data.route;
                            self.form.head = data.headers;
                            self.form.domain = data.domain;
                            self.form.isClearCookie = data.isClearCookie;
                            self.form.description = data.description;
                            // 加后缀ww
                            data.setGlobalVars.forEach((setGlobalVar) => {
                              setGlobalVar.query = this.addSuffix(setGlobalVar.query)
                            });

                            self.form.setGlobalVars = data.setGlobalVars;

                            try {
                                self.form.parameterRaw = JSON.stringify(data.presendParams);
                                self.form.parameterRaw = self.form.parameterRaw.replace(/'/g, "\"").replace(/None/g, "null").replace(/True/g, "true").replace(/False/g, "false");
                                if (self.form.parameterRaw === '{}'){
                                  self.form.parameterRaw = ''
                                }
                            } catch (e){
                              self.$message.error({
                                message: '获取请求参数出现异常！' + e,
                                center: true,
                              });
                            }
                            self.form.checkHttp = data.checkHttpCode;

                            if (data.checkResponseData === null || data.checkResponseData === undefined){
                              self.form.checkRegex = [{regex: "", query: []}]
                            }
                            else{
                              // 加后缀
                              data.checkResponseData.forEach((data) => {
                                data.query = this.addSuffix(data.query);
                              });
                              self.form.checkRegex = data.checkResponseData;
                            }

                            if (data.checkResponseNumber === null || data.checkResponseNumber === undefined){
                              self.form.checkNumber = [{expressions:{'firstArg': '', 'operator': '', 'secondArg': '', 'judgeCharacter': '', 'expectResult': ''}}]
                            }else{
                              self.form.checkNumber = data.checkResponseNumber
                            }

                            if (data.checkResponseSimilarity === null || data.checkResponseSimilarity === undefined){
                              self.form.checkSimilarity = [{'baseText': '', 'compairedText': '', 'targetSimilarity': null}]
                            }else{
                              self.form.checkSimilarity = data.checkResponseSimilarity
                            }

                          }else {
                            self.$message.error({
                                message: data,
                                center: true,
                            });
                        }
                }).catch((error) => {
                  self.$message.error({
                      message: '接口用例详情获取失败，请稍后刷新重试哦~',
                      center: true,
                  });
                  self.listLoading = false;
                })
            },
            addSuffix(query){
              const isValidQuery = query.constructor === Array && query.length > 0;
              if (isValidQuery){
                query.forEach((item, index) => {
                  const suffixStartIndex = item.search(/\([0-9]+\)/);
                  const expectedSuffix = '(' + (index + 1).toString() + ')';
                  if (suffixStartIndex === -1){
                    query[index] = item + expectedSuffix;
                  }else{
                    query[index] = item.substring(0, suffixStartIndex) + expectedSuffix;
                  }
                })
              }
              return query
            }
        },
        watch: {
            radio() {
                this.changeParameterType()
            },
            form: {
                //注意：当观察的数据为对象或数组时，curVal和oldVal是相等的，因为这两个形参指向的是同一个数据对象
                handler(curVal,oldVal){
                    if (curVal.check === 'noCheck') {
                        this.showHttpCodeCheck = false
                        this.showJsonRegexCheck = false
                        this.showNumberCheck = false
                        this.showSimilarityCheck = false
                    } else if (curVal.check === 'checkHttpStatusCode') {
                        this.showHttpCodeCheck = true
                        this.showJsonRegexCheck = false
                        this.showNumberCheck = false
                        this.showSimilarityCheck = false
                    } else if (curVal.check === 'checkJsonRegex'){
                        this.showHttpCodeCheck = false
                        this.showJsonRegexCheck = true
                        this.showNumberCheck = false
                        this.showSimilarityCheck = false
                    } else if (curVal.check === 'checkNumber'){
                        this.showHttpCodeCheck = false
                        this.showJsonRegexCheck = false
                        this.showNumberCheck = true
                        this.showSimilarityCheck = false
                    } else if (curVal.check === 'checkSimilarity'){
                        this.showHttpCodeCheck = false
                        this.showJsonRegexCheck = false
                        this.showNumberCheck = false
                        this.showSimilarityCheck = true
                    }
                },
                deep:true
            },
        },
        mounted() {
            this.getCaseApiInfo()
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
    .head-class {
        font-size: 17px
    }
    .parameter-a {
        display: block;
    }
    .parameter-b {
        display: none;
    }
    .selectInput {
        position: absolute;
        /*margin-left: 7px;*/
        padding-left: 9px;
        width: 180px;
        /*border-radius:0px;*/
        /*height: 38px;*/
        left: 1px;
        border-right: 0px;
    }
</style>
<style lang="scss">
    .selectInput{
        input{
            border-right: 0px;
            border-radius: 4px 0px 0px 4px;
        }
    }
</style>
