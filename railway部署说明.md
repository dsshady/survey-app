# Railway 部署说明

本文档将指导您如何将问卷系统部署到 [Railway](https://railway.app/) 平台。

## 部署前准备

请确保项目目录中包含以下必要文件：
- `app_cloud.py`: 应用主文件
- `survey_final.html`: 问卷页面文件
- `requirements.txt`: Python 依赖包列表
- `Procfile`: 应用启动配置文件

## 部署步骤

### 1. 注册 Railway 账号
访问 [Railway官网](https://railway.app/) 并注册账号。

### 2. 准备代码仓库
Railway 推荐通过 GitHub 仓库进行部署。请将项目代码上传到 GitHub：
- 在 GitHub 上创建一个新的仓库
- 将本地项目代码推送到该仓库

### 3. 从 GitHub 部署
1. 登录 Railway 控制台
2. 点击 "Deploy from GitHub Repo"
3. 授权 Railway 访问你的 GitHub 账户，并选择包含问卷系统的仓库
4. Railway 会自动检测项目类型并根据 `requirements.txt` 构建环境

### 4. 配置环境变量
在 Railway 控制台中设置以下环境变量：
- `INITIATOR_SECRET`: 用于访问结果页面的安全密钥（建议使用复杂字符串）
- `PORT`: Railway 自动分配的端口（通常不需要手动设置）

### 5. 重新部署
由于我们修改了配置文件，需要重新部署应用：
1. 在 Railway 控制台中找到你的项目
2. 点击 "Deploy" 按钮触发重新部署
3. 等待构建和部署完成

## 访问应用

- 问卷填写页面: `https://your-app-url.railway.app`
- 结果查看页面: `https://your-app-url.railway.app?secret=YOUR_SECRET_KEY` (请替换 YOUR_SECRET_KEY 为你设置的环境变量值)

## 注意事项

1. 数据存储: 当前版本的数据存储在本地 JSON 文件中，每次重新部署可能会丢失数据。建议后续改用数据库存储。
2. 日志查看: 可在 Railway 控制台中查看应用运行日志。