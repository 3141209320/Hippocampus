# 🔧 Render 数据持久化解决方案

## 问题说明

你遇到的问题是 Render 免费层的**临时文件系统**导致的:

### 现象
- ✅ 昨晚部署后可以正常使用
- ❌ 今早打开网站需要重新部署
- ❌ 昨晚上传的 txt 文件消失了
- ❌ 昨晚创建的用户也不见了

### 原因
1. **Render 免费层会自动休眠**: 15分钟无访问后服务会休眠
2. **唤醒时文件系统重置**: 休眠后再次访问会重启服务,文件系统会被重置
3. **SQLite 数据库丢失**: `db.sqlite3` 文件在临时文件系统上,重启后消失
4. **上传文件丢失**: `media/` 文件夹中的上传文件也会消失

---

## 🎯 解决方案: 使用 PostgreSQL 数据库

### 为什么选择 PostgreSQL?
- ✅ **数据持久化**: Render 提供的 PostgreSQL 数据库是持久化的
- ✅ **免费**: Render 提供免费的 PostgreSQL 数据库(90天后会删除,但可以重新创建)
- ✅ **生产级**: PostgreSQL 比 SQLite 更适合生产环境
- ✅ **自动备份**: Render 会自动备份数据库

---

## 📋 迁移步骤

### 第一步: 在 Render 创建 PostgreSQL 数据库

1. **登录 Render Dashboard**
   - 访问 https://dashboard.render.com/

2. **创建新的 PostgreSQL 数据库**
   - 点击 "New +" 按钮
   - 选择 "PostgreSQL"

3. **配置数据库**
   - Name: `hippocampus-db` (或任何你喜欢的名字)
   - Database: `hippocampus` (自动生成)
   - User: `hippocampus` (自动生成)
   - Region: 选择与你的 Web Service 相同的区域
   - PostgreSQL Version: 选择最新版本
   - Plan: **Free** (免费)

4. **创建数据库**
   - 点击 "Create Database"
   - 等待几分钟,数据库创建完成

5. **复制数据库连接信息**
   - 创建完成后,进入数据库详情页
   - 找到 "Connections" 部分
   - 复制 **Internal Database URL** (类似: `postgresql://user:password@hostname/database`)

### 第二步: 更新项目代码

代码已经为你准备好了,只需要推送到 GitHub:

1. **查看更新的文件**
   - `hippocampus_project/settings.py` - 已配置 PostgreSQL
   - `requirements.txt` - 已添加 `psycopg2-binary`

2. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Switch to PostgreSQL for persistent storage"
   git push
   ```

### 第三步: 在 Render 配置环境变量

1. **进入你的 Web Service**
   - 在 Render Dashboard 中,点击你的 `hippocampus-app` 服务

2. **添加环境变量**
   - 点击左侧 "Environment" 标签
   - 点击 "Add Environment Variable"
   - 添加以下变量:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | 粘贴第一步复制的 Internal Database URL |

3. **保存并重新部署**
   - 点击 "Save Changes"
   - Render 会自动重新部署

### 第四步: 等待部署完成

- 部署需要 3-5 分钟
- 部署完成后,数据库会自动迁移
- 管理员账号会自动创建(用户名: `admin`, 密码: `admin123456`)

---

## 🎉 完成!

现在你的应用已经使用持久化的 PostgreSQL 数据库了!

### 测试验证

1. **访问你的网站**
2. **用管理员账号登录** (admin / admin123456)
3. **上传一个试卷**
4. **等待 20 分钟** (让服务自动休眠)
5. **再次访问网站**
6. **检查数据是否还在** ✅

---

## ⚠️ 关于上传文件的说明

### 当前状态
- 数据库数据已持久化 ✅
- 上传的文件仍然会丢失 ❌

### 为什么?
- Render 免费层的文件系统仍然是临时的
- `media/` 文件夹中的文件会在重启后消失

### 解决方案(可选)

如果你需要持久化上传的文件,有两个选择:

#### 选项 1: 使用 Render Disk (付费)
- 费用: $1/月 起
- 配置简单,直接挂载持久化磁盘

#### 选项 2: 使用云存储 (推荐)
- 使用 AWS S3, Cloudinary, 或 Backblaze B2
- 免费额度通常够用
- 需要修改代码配置

**对于你的应用**:
- 如果上传的试卷文件不多,可以在每次重启后重新上传
- 或者考虑将试卷内容直接存储在数据库中(而不是文件)

---

## 📊 Render 免费层限制

### PostgreSQL 免费数据库
- ✅ 数据持久化
- ✅ 1GB 存储空间
- ⚠️ 90天后会被删除(但可以重新创建)
- ⚠️ 删除前会提前通知

### Web Service 免费层
- ✅ 代码和数据库数据持久化
- ❌ 文件系统临时(重启后重置)
- ⚠️ 15分钟无访问会休眠
- ⚠️ 每月 750 小时免费运行时间

---

## 🔐 安全建议

1. **修改默认管理员密码**
   - 首次登录后立即修改
   - 访问 `/admin` 修改密码

2. **保护数据库 URL**
   - 不要将 `DATABASE_URL` 提交到 Git
   - 只在 Render 环境变量中配置

3. **定期备份**
   - Render 会自动备份,但建议定期手动导出数据
   - 使用 `python manage.py dumpdata > backup.json`

---

## ❓ 常见问题

### Q: 迁移到 PostgreSQL 后,本地开发怎么办?
**A**: 本地仍然使用 SQLite,不受影响。代码会自动检测:
- 如果有 `DATABASE_URL` 环境变量 → 使用 PostgreSQL
- 如果没有 → 使用 SQLite

### Q: 90天后数据库被删除怎么办?
**A**: 
1. Render 会提前通知你
2. 你可以导出数据: `python manage.py dumpdata > backup.json`
3. 创建新的免费数据库
4. 导入数据: `python manage.py loaddata backup.json`

### Q: 上传的文件还是会丢失怎么办?
**A**: 有三个选择:
1. 每次重启后重新上传(如果文件不多)
2. 使用 Render Disk ($1/月)
3. 使用云存储服务(如 Cloudinary 免费版)

### Q: 如何查看数据库中的数据?
**A**: 
1. 在 Render Dashboard 中进入你的 PostgreSQL 数据库
2. 点击 "Connect" 查看连接信息
3. 使用 pgAdmin 或其他 PostgreSQL 客户端连接

---

## 📞 需要帮助?

如果遇到问题,请提供:
1. 错误信息截图
2. Render 部署日志
3. 具体的问题描述

祝使用愉快! 🎉
