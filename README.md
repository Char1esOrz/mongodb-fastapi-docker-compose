# mongodb-fastapi-docker-compose
 A mongodb api service using fastapi, deployed using docker-compose


## Installation ( Quick Start )

```shell
git clone https://github.com/Char1esOrz/mongodb-fastapi-docker-compose
```
```shell
cd mongodb-fastapi-docker-compose
```
```shell
cp .env.example .env
```
Now you can modify the .env file to set the parameters of mongodb and fastapi
```shell
vim .env
```
如果你在国内,请修改Dockerfile 增加 -i https://pypi.tuna.tsinghua.edu.cn/simple
```
vim .env
#修改
RUN pip install --no-cache-dir -r requirements.txt
# 为
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
Run
```shell
docker compose up
```
Open the server by clicking on the following link: [http://localhost:8000/docs](http://localhost:8000/docs)
