# 🚀 快速修复指南 - 解决数据丢失问题

## 问题
- ✅ 昨晚部署后可以使用
- ❌ 今早打开需要重新部署
- ❌ 上传的文件和用户都不见了

## 原因
Render 免费层使用**临时文件系统**,服务休眠后重启会重置所有数据。

## 解决方案
使用 **PostgreSQL 持久化数据库**

---

## 📋 操作步骤(5分钟完成)

### 1️⃣ 在 Render 创建 PostgreSQL 数据库

1. 访问 https://dashboard.render.com/
2. 点击 **"New +"** → 选择 **"PostgreSQL"**
3. 配置:
   - **Name**: `hippocampus-db`
   - **Region**: 选择与你的 Web Service 相同的区域
   - **PostgreSQL Version**: 16 (最新版)
   - **Plan**: **Free** ✅
4. 点击 **"Create Database"**
5. 等待创建完成(约1-2分钟)

### 2️⃣ 复制数据库连接 URL

1. 进入刚创建的数据库页面
2. 找到 **"Connections"** 部分
3. 复制 **"Internal Database URL"**
   - 格式类似: `postgresql://user:pass@hostname/dbname`
   - ⚠️ 注意: 要复制 **Internal** URL,不是 External

### 3️⃣ 配置环境变量

1. 回到你的 **Web Service** (`hippocampus-app`)
2. 点击左侧 **"Environment"** 标签
3. 点击 **"Add Environment Variable"**
4. 添加:
   - **Key**: `DATABASE_URL`
   - **Value**: 粘贴刚才复制的 Internal Database URL
5. 点击 **"Save Changes"**

### 4️⃣ 推送代码到 GitHub

```bash
git add .
git commit -m "Add PostgreSQL support for persistent storage"
git push
```

### 5️⃣ 等待部署完成

- Render 会自动检测到代码更新并重新部署
- 等待 3-5 分钟
- 部署完成后,数据库会自动迁移
- 管理员账号会自动创建

---

## ✅ 验证是否成功

1. **访问你的网站**
2. **登录** (用户名: `admin`, 密码: `admin123456`)
3. **上传一个试卷**
4. **等待 20 分钟**(让服务休眠)
5. **再次访问网站**
6. **检查数据是否还在** ✅

如果数据还在,说明成功了! 🎉

---

## 📝 重要说明

### ✅ 已解决的问题
- 用户数据会持久化保存
- 试卷题目会持久化保存
- 不需要每次都重新部署

### ⚠️ 仍然存在的问题
- **上传的 .txt 文件**仍然会在重启后丢失
- 但是**题目内容已经保存在数据库中**,不受影响

### 💡 为什么上传的文件会丢失?
- 文件存储在 `media/` 文件夹
- Render 免费层的文件系统是临时的
- 但题目内容已经解析并保存到数据库了,所以不影响使用

### 🔧 如果需要持久化文件
有两个选择:
1. **Render Disk** (付费, $1/月起)
2. **云存储** (如 Cloudinary, 有免费额度)

---

## 🆘 遇到问题?

### 问题: 部署失败
**检查**:
- 确认 `DATABASE_URL` 环境变量已正确设置
- 查看 Render 部署日志中的错误信息

### 问题: 无法连接数据库
**检查**:
- 确认复制的是 **Internal Database URL**
- 确认数据库和 Web Service 在**同一个 Region**

### 问题: 数据还是丢失
**检查**:
- 确认代码已推送到 GitHub
- 确认 Render 已重新部署
- 查看环境变量是否正确设置

---

## 📞 需要更详细的说明?

查看 `PERSISTENT_STORAGE_GUIDE.md` 获取完整指南。
