# Taisite-Platform

![](https://img.shields.io/badge/-%20marvelous-orange) ![](https://img.shields.io/badge/-%20gogeous-grey) ![](https://img.shields.io/badge/-%20elegant-blue)   

+ [Taisite-Platform 中文文档](https://github.com/amazingTest/Taisite-Platform/blob/master/README_CN.md)

![泰斯特平台LOGO.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/泰斯特平台LOGO.png)

## Ⅰ. Introduction

### Background

"Taisite-Platform" is an interface automation test platform developed by "Software Testing & Machine Learning Enthusiasts".

### Vision

The platform is dedicated to effectively combining artificial intelligence technology with software testing, enabling 
the platform to be more intelligent and generalized while ensuring test accuracy requirements
and **optimize the user experience** at the same time. The goal is to become the most intimate, best-used, 
highest value open source test platform.
 
### Technology stack

The platform follows the idea of "separate development frontend and backend". The technology stack is: "Python + Vue + Mongodb".
 
 [***（Thanks for the inspiration that this open source project brought to me.)***](https://github.com/githublitao/api_automation_test) 

### User environment

**Chrome is a good choice**

### Open source protocol

***APGL-3.0***


## Ⅱ. Taisite-platform features (os: What is the difference between other test platforms?)

 **0. It has been put into production environment for more than 1 year, it is stable~**
 
 1. The platform follows a "small but fine" strategy to maximize the development of all features and cost-effectiveness, helping test teams quickly build easy-to-follow/maintain interfaces
  automated test system.
 
 2. The platform follows the "zero-encoding" principle, and users can complete more complex business process interface tests without programming.
 
 3. The platform follows the principle of “good-looking is justice” and the operation interface is shown as follows:
 
 ![操作界面展示](https://github.com/amazingTest/Taisite-Platform/blob/master/images/操作界面展示.png)
 
 4. The platform has an excellent timed task experience. After starting the scheduled task, you can disable/arbitrarily edit the task content and take effect immediately. It also has a rich alarm strategy.
  The page is shown below:
 
 ![定时任务配置](https://github.com/amazingTest/Taisite-Platform/blob/master/images/定时任务配置.png)
 
 5. The platform has import/export capabilities that support testers **"favorite"** Excel format for easy batch generation/modification of use cases.
 
 ![数据导入展示](https://github.com/amazingTest/Taisite-Platform/blob/master/images/数据导入展示.png)
 
 6. The platform has a rich test result verification system and supports **text similarity** verification.
 ([get more detail](https://juejin.im/post/5cfe1dd96fb9a07ed7407321))
 
 7. The platform provides a test task scheduling interface to facilitate integration with development projects.
 
 8. ......
 
 ***（There are so many amazing little features waiting for you to explore & tap）***
 

## Ⅲ .Taisite-platform function diagram

### V1.0

![泰斯特平台结构图_V1.0](https://github.com/amazingTest/Taisite-Platform/blob/master/images/泰斯特平台结构图_V1.0.png)

## IV . Deploy

### Deploy under windows 

#### 0. Clone

    git clone https://github.com/amazingTest/Taisite-Platform.git

#### 1. Install python 3 env

#### 2. 部署自然语言模型

[Download model](https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip)

2.2 Extract the compression package

2.3 Install python dependent-packages

    pip install tensorflow==1.14.0  -i https://pypi.tuna.tsinghua.edu.cn/simple
    pip install bert-serving-server==1.9.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
  
2.4 Start the model

// Execute after the current directory is switched to the model folder directory

    bert-serving-start -model_dir ./chinese_L-12_H-768_A-12/ -num_worker=1
  
After the startup is successful, the output is as follows:

![NLP模型启动成功输出](https://github.com/amazingTest/Taisite-Platform/blob/master/images/NLP模型启动成功输出.png)    

#### 3. Deploy Mongodb database

#### 4. Set system environment variables

    AUTOTEST_PLATFORM_ENV=production
    AUTOTEST_PLATFORM_NLP_SERVER_HOST=127.0.0.1
    AUTOTEST_PLATFORM_MONGO_HOST=${MONGO_HOST}
    AUTOTEST_PLATFORM_MONGO_PORT=${MONGO_PORT}
    AUTOTEST_PLATFORM_MONGO_USERNAME=${USERNAME}
    AUTOTEST_PLATFORM_MONGO_PASSWORD=${PASSWORD}
    AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME=taisite
  
Where AUTOTEST_PLATFORM_ENV defaults to production (required)

AUTOTEST_PLATFORM_MONGO_HOST and AUTOTEST_PLATFORM_MONGO_PORT indicate the address and port of the database (required)

AUTOTEST_PLATFORM_MONGO_USERNAME and AUTOTEST_PLATFORM_MONGO_PASSWORD represent the account password of the database (if not required)

AUTOTEST_PLATFORM_NLP_SERVER_HOST (Natural Language Model Service) defaults to native boot (not required)

AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME is the default data table name (required)

After the setting is completed, you can test it with the following commands (CMD switches to the project root directory)

    python ./backend/config.py
  
If the configuration is successful, you can see the input configuration data.

#### 5. Package the front-end dist file (I have done this for you, skip it if you don't need secondary development)

5.1 Install the Vue environment, download node.js and configure the environment, download the npm package manager

5.2 Cmd into the frontend directory, configure cnpm:

    npm install -g cnpm --registry=https://registry.npm.taobao.org   
  
5.3 Execute the install dependency package command:

    cnpm install
  
5.4 Execute the package command:

    cnpm run build
  
If successfully packaged, the dist folder will be generated in the project root directory.

#### 6. Start backend

// Switch to the project root directory to execute

    pip install -r ./backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

// Start backend (default 5050 port)

    python ./backend/run.py

// Create a platform administrator account password

    python ./backend/createAdminUser.py
  
#### 7. Access project

You can now log in using http://127.0.0.1:5050/#/login using the created administrator account password.

![平台登录界面2.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/平台登录界面2.png)

### Docker containerized deployment in Linux environment

#### 0. Clone

    git clone https://github.com/amazingTest/Taisite-Platform.git
  
#### 1. Natural language model deployment

    sudo -i
    docker pull shaoyuyishiwo/bertserver
    docker run --name autotest-platform-bertserver -d shaoyuyishiwo/bertserver 


#### 2. Mongo database deployment (skip this step if an existing database is available)

2.1 Start database & data mount to host

    sudo -i
    docker pull mongo 
    docker run  --name autotest-platform-mongo -p 27017:27017 -v /data/db:/data/db -v /data/configdb:/data/configdb ``-d mongo
  
2.2 Create a database account

    docker exec -it autotest-platform-mongo /bin/bash

    mongo

    > use admin

    switched to db admin

    > db.createUser({user:"${USERNAME}",pwd:"${PASSWORD}",roles:["root"]})

    Successfully added user: { "user" : "admin", "roles" : [ "root" ] }
  
2.3 Database memory expansion (recommended)

    > db.adminCommand({setParameter:1, internalQueryExecMaxBlockingSortBytes:335544320})

    { "was" : 33554432, "ok" : 1 }
  
#### 3. Environment variable configuration

// 编辑 /etc/profile 文件

    sudo -i
    vi /etc/profile
  
If there is a warning, select (E)dit anyway (enter E)

3.1 Insert the following data at the end of the text (enter i to get into insert status)

    export AUTOTEST_PLATFORM_ENV=production
    export AUTOTEST_PLATFORM_NLP_SERVER_HOST=${BERT_IPADRESS}
    export AUTOTEST_PLATFORM_MONGO_HOST=${MONGO_HOST}
    export AUTOTEST_PLATFORM_MONGO_PORT=${MONGO_PORT}
    export AUTOTEST_PLATFORM_MONGO_USERNAME=${USERNAME}
    export AUTOTEST_PLATFORM_MONGO_PASSWORD=${PASSWORD}
    export AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME=${DBNAME}

The variable is a dynamic value. The deployer can input it according to the actual situation. 
The DBNAME value can be arbitrarily customized (database table name). The BERT_IPADRESS and 
MONGO_HOST values can be queried by the following commands:

    docker inspect autotest-platform-bertserver
    docker inspect autotest-platform-mongo // If you used the above steps to deploy the database
  
The output is shown below:

![控制台输出1.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/控制台输出1.png)

3.2 After inserting, click the ESC button, type :wq and click Enter to save.

3.3 Environment variables take effect immediately after executing the following command

    source /etc/profile
  
#### 4. Start the project

Before you start the project, you need to change the timezone info by modifying the RUN script in **Dockerfile.backend** which stay 
in first-level directory of the project. The default timezone is Asia/Shanghai.

// Execute the deployment file in the project root directory

    sh deploy ${PORT} 
  
The ${PORT} variable fills in the project access port, and the administrator account password is also created when the 
project starts, as shown in the following figure:

![控制台输出2.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/控制台输出2.png)

#### 5. Access project

The browser can access the ${PORT} port of the deployment server address.

![平台登录界面.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/平台登录界面.png)


#### EXTRA. FQA

The following output represents the NLP model startup failure

![NLP部署失败.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/NLP部署失败.png) 

Solution steps:

1. Remove the code from ./backend/app/init.py:

![不使用NLP模型方法指南1.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/不使用NLP模型方法指南1.png)

2. Modify the following code in ./backend/testframe/interfaceTest/tester.py to pass:

![不使用NLP模型方法指南2.png](https://github.com/amazingTest/Taisite-Platform/blob/master/images/不使用NLP模型方法指南2.png)

When you start the project after you finish, you will not depend on the natural language model~

## V . Contact me

if you have any questions feel free to email me , 523314409@qq.com.




