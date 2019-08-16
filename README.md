# Taisite-Platform

## 项目简介

Helping software testing is my duty


## 项目部署

### Docker 中部署 

[Docker 安装指南](https://www.runoob.com/docker/ubuntu-docker-install.html)

#### 语言模型部署

	sudo -i
	docker pull shaoyuyishiwo/bertserver
	docker run --name autotest-platform-bertserver -d shaoyuyishiwo/bertserver 

#### Mongo 数据库部署 (若已有现成数据库可用则可跳过此步)
  
##### 启动数据库 & 数据挂载至宿主机
    
    sudo -i
    docker pull mongo 
    docker run  --name autotest-platform-mongo -p 27017:27017 -v /data/db:/data/db -v /data/configdb:/data/configdb ``-d mongo
  
##### 创建数据库帐号

	docker exec -it autotest-platform-mongo /bin/bash

	> use admin
  
	switched to db admin
  
    > db.createUser({user:"${USERNAME}",pwd:"${PASSWORD}",roles:["root"]})
  
	Successfully added user: { "user" : "admin", "roles" : [ "root" ] }

##### 数据库内存扩容(建议)
  
    > db.adminCommand({setParameter:1, internalQueryExecMaxBlockingSortBytes:335544320})
    
    { "was" : 33554432, "ok" : 1 }
 

#### 环境变量配置
  
    sudo -i
    vi /etc/profile
  
  若出现警告则选择 (E)dit anyway (输入 E)
  
  ##### 文本末端插入 (输入 i 则变为 insert 状态)
  
    export AUTOTEST_PLATFORM_NLP_HOST=${BERT_IPADRESS}
    export AUTOTEST_PLATFORM_MONGO_HOST=${MONGO_HOST}
    export AUTOTEST_PLATFORM_MONGO_PORT=27017
    export AUTOTEST_PLATFORM_MONGO_USERNAME=${USERNAME}
    export AUTOTEST_PLATFORM_MONGO_PASSWORD=${PASSWORD}
    export AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME=attest
	
  其中 ${BERT_IPADRESS} 和 ${MONGO_HOST} 值可通过下列命令找到：
  
    docker inspect autotest-platform-bertserver
    docker inspect autotest-platform-mongo
  
  输出如下图所示：
  
  ![image](https://github.com/amazingTest/Taisite-Platform/blob/master/images/001.png)
  
  ##### 插入完毕后点击 ESC 按钮、输入 :wq 后单击回车保存
  
  ##### 执行下列命令后环境变量立即生效
 
    source /etc/profile

#### 启动项目

    git clone https://github.com/amazingTest/Taisite-Platform.git
    sh deploy ${PORT} (如: sh deploy 5050)
    
  部署的同时也创建的管理员帐号，如下图所示：
  
  ![image](https://github.com/amazingTest/Taisite-Platform/blob/master/images/002.png)
  
#### 访问项目

浏览器访问部署服务器地址的 ${PORT} 端口
使用「启动项目」中创建的帐号密码登陆即可


    
    
