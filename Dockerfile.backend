FROM python:3.6

USER root

ENV WORKING_DIR /app/AutoTest-Platform

ENV AUTOTEST_PLATFORM_ENV=${AUTOTEST_PLATFORM_ENV}
ENV AUTOTEST_PLATFORM_MONGO_HOST=${AUTOTEST_PLATFORM_MONGO_HOST}
ENV AUTOTEST_PLATFORM_MONGO_PORT=${AUTOTEST_PLATFORM_MONGO_PORT}
ENV AUTOTEST_PLATFORM_MONGO_USERNAME=${AUTOTEST_PLATFORM_MONGO_USERNAME}
ENV AUTOTEST_PLATFORM_MONGO_PASSWORD=${AUTOTEST_PLATFORM_MONGO_PASSWORD}
ENV AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME=${AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME}

COPY backend/utils /${WORKING_DIR}/backend/utils
COPY backend/testframe /${WORKING_DIR}/backend/testframe

COPY backend/requirements.txt /${WORKING_DIR}/backend/requirements.txt
COPY backend/config.py /${WORKING_DIR}/backend/config.py
COPY backend/app /${WORKING_DIR}/backend/app
COPY backend/controllers /${WORKING_DIR}/backend/controllers
COPY backend/models /${WORKING_DIR}/backend/models
COPY backend/createAdminUser.py /${WORKING_DIR}/backend/createAdminUser.py
COPY backend/run.py /${WORKING_DIR}/backend/run.py
COPY ./dist /${WORKING_DIR}/dist

RUN sh -c "echo 'Asia/Shanghai' > /etc/timezone" \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && export AUTOTEST_PLATFORM_ENV=${AUTOTEST_PLATFORM_ENV}\
    && export AUTOTEST_PLATFORM_MONGO_HOST=${AUTOTEST_PLATFORM_MONGO_HOST}\
    && export AUTOTEST_PLATFORM_MONGO_PORT=${AUTOTEST_PLATFORM_MONGO_PORT}\
    && export AUTOTEST_PLATFORM_NLP_SERVER_HOST=${AUTOTEST_PLATFORM_NLP_SERVER_HOST}\
    && export AUTOTEST_PLATFORM_MONGO_USERNAME=${AUTOTEST_PLATFORM_MONGO_USERNAME}\
    && export AUTOTEST_PLATFORM_MONGO_PASSWORD=${AUTOTEST_PLATFORM_MONGO_PASSWORD}\
    && export AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME=${AUTOTEST_PLATFORM_MONGO_DEFAULT_DBNAME}\
    && pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple\
    && cd ${WORKING_DIR}/backend\
    && pip install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT cd ${WORKING_DIR}/backend; python createAdminUser.py; python run.py;








