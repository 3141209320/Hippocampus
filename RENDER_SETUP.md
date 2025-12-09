# Render 部署后的初始化指南

## ⚠️ 重要说明

Render 上的数据库是**全新的空数据库**，与您本地的 `db.sqlite3` 完全独立。这意味着：

1. ❌ 本地创建的 admin 账号在 Render 上不存在
2. ❌ 本地上传的试卷在 Render 上看不到
3. ❌ 本地的用户数据在 Render 上都没有

**这是正常的！** 每个环境都有自己独立的数据库。

---

## 🔧 解决方案：在 Render 上创建管理员账号

### ⭐ 方法一：自动创建（最简单，推荐！）

我已经为您添加了自动创建管理员的功能！

**默认管理员账号**：
- 用户名：`admin`
- 密码：`admin123456`

**使用步骤**：
1. 将更新后的代码推送到 GitHub：
   ```bash
   git add .
   git commit -m "Add auto admin creation"
   git push
   ```

2. Render 会自动重新部署（等待 3-5 分钟）

3. 部署完成后，直接用以下账号登录：
   - 用户名：`admin`
   - 密码：`admin123456`

4. **重要**：登录后请立即修改密码！
   - 访问 `https://你的网址/admin`
   - 登录后点击右上角修改密码

**自定义管理员账号**（可选）：
如果您想自定义用户名和密码，在 Render Dashboard 中设置环境变量：
- `ADMIN_USERNAME` = 您想要的用户名
- `ADMIN_PASSWORD` = 您想要的密码
- `ADMIN_EMAIL` = 您的邮箱

---

### 方法二：使用 Render Shell（如果有的话）

1. **登录 Render Dashboard**
   - 访问 [render.com](https://render.com/)
   - 进入您的 `hippocampus-app` 服务

2. **打开 Shell**
   - 点击右上角的 **"Shell"** 按钮
   - 会打开一个终端界面

3. **创建超级用户**
   在 Shell 中输入以下命令：
   ```bash
   python manage.py createsuperuser
   ```

4. **按提示输入信息**
   ```
   Username: admin
   Email address: (可以留空，直接回车)
   Password: (输入密码，不会显示)
   Password (again): (再次输入密码)
   ```

5. **完成！**
   现在您可以用 `admin` 账号登录 Render 上的网站了。

---

### 方法二：通过环境变量自动创建（高级）

如果您想在每次部署时自动创建管理员账号，可以：

1. 在 Render Dashboard 中设置环境变量：
   - `DJANGO_SUPERUSER_USERNAME=admin`
   - `DJANGO_SUPERUSER_PASSWORD=你的密码`
   - `DJANGO_SUPERUSER_EMAIL=admin@example.com`

2. 修改 `build.sh`，添加自动创建命令（但这样密码会暴露在代码中，不推荐）

---

## 📤 关于试卷数据

### 为什么看不到本地的试卷？

因为 Render 使用的是独立的数据库。您有两个选择：

### 选项 1：在 Render 上重新上传试卷（推荐）

1. 用管理员账号登录 Render 网站
2. 点击"上传试卷"
3. 重新上传您的试卷文件
4. 系统会自动解析并创建题库

**优点**：简单、安全、符合正常使用流程

### 选项 2：迁移本地数据到 Render（复杂，不推荐）

需要：
1. 导出本地数据（`python manage.py dumpdata`）
2. 上传到 Render
3. 在 Render Shell 中导入（`python manage.py loaddata`）

**缺点**：复杂、容易出错、文件路径可能有问题

---

## 🎯 推荐的工作流程

### 本地开发环境
- 用于开发和测试
- 数据库：`db.sqlite3`（本地文件）
- 可以随意创建测试数据

### Render 生产环境
- 用于正式使用
- 数据库：Render 提供的独立数据库
- 只保存真实的用户数据和试卷

### 两者关系
- **代码同步**：通过 Git 推送到 GitHub，Render 自动部署
- **数据独立**：数据库完全独立，互不影响

---

## 📝 常见问题

### Q1: 我在本地创建的用户，为什么在 Render 上登录不了？
**A**: 因为数据库是独立的。您需要在 Render 上重新注册或创建用户。

### Q2: 我想让 Render 和本地使用同一个数据库可以吗？
**A**: 技术上可以（使用云数据库如 PostgreSQL），但不推荐。正确的做法是：
- 本地：用于开发测试
- Render：用于生产环境
- 两者数据独立

### Q3: 每次部署都要重新创建管理员吗？
**A**: 不需要！Render 的数据库是持久化的。您只需要创建一次管理员，以后就一直存在。

### Q4: 如果我更新了代码，数据会丢失吗？
**A**: 不会！更新代码不会影响数据库。您的用户、试卷等数据都会保留。

---

## ✅ 快速操作步骤

1. **在 Render Shell 中创建管理员**
   ```bash
   python manage.py createsuperuser
   ```

2. **用管理员登录 Render 网站**
   - 访问您的 Render 网址
   - 用刚创建的 admin 账号登录

3. **上传试卷**
   - 点击"上传试卷"
   - 上传您的 `.txt` 试卷文件

4. **开始使用！**
   - 现在可以正常刷题了
   - 其他用户注册后也能看到您上传的试卷

---

## 🔐 安全建议

1. **生产环境密码**：Render 上的管理员密码要设置得复杂一些
2. **不要在代码中硬编码密码**
3. **定期备份重要数据**（可以用 Django 的 dumpdata 命令）

---

有问题随时联系！
