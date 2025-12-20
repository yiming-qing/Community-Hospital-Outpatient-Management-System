# 社区医院门诊管理系统（数据库系统实验大作业）

本项目实现《实验考察1.pdf》中的“社区医院门诊管理系统”参考数据库需求：患者网上预约、到院登记/签到、就诊状态流转、缴费结算、排班管理与统计查询。

## 环境要求

- MySQL 8.0（作业要求，需提前启动 MySQL 服务）
- Python 3（用于 Flask 后端）
- Node.js + npm（用于 Vue3 前端）
- Windows PowerShell 5.1+（本仓库提供一键启动脚本 `start.ps1`）

## 目录结构

- `backend/`：Flask 后端（REST API + JWT）
- `frontend/`：Vue3 + Element Plus 前端（患者端 + 前台端）
- `database/`：MySQL 8.0 建表/初始化/测试数据脚本
- `PLAN.md`：实现计划与需求对照
- `docs/系统分析与设计.md`：系统分析与总体设计文档
- `docs/数据库设计.md`：数据库设计文档

## 访问地址

- 前端：`http://localhost:5173`
- 后端：`http://localhost:5000`（一般无需直接打开，前端通过 `/api` 代理访问）

系统通过“登录账号的角色”自动分流：访问 `/` 会跳转到该角色的默认工作台（患者/前台/管理员）。

## 一键启动（MySQL）

在项目根目录执行（会：初始化 MySQL 数据库 + 写入 `backend/.env` + 启动前后端）：

```powershell
.\start.ps1 -MySqlUser root -MySqlHost 127.0.0.1 -MySqlPort 3306
```

常用参数：

- `-MySqlExePath "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"`：当 `mysql.exe` 不在 PATH 时使用
- `-MySqlPassword your_password`：不想交互输入密码时使用（注意：会以明文写入 `backend/.env`，且可能出现在 PowerShell 历史记录）
- `-IncludeTestData`：额外导入 `database/test_data.sql`
- `-AutoSeed`：写入 `AUTO_SEED=1`，启动后端时自动补齐演示数据（一般不建议与“严格 SQL 初始化”混用）

提示：

- 若 PowerShell 阻止脚本运行，可使用：`powershell -ExecutionPolicy Bypass -File .\start.ps1 ...`
- 首次运行会创建 `backend/.venv` 并安装依赖、以及在 `frontend/` 执行 `npm install`，需要等待几分钟

停止方式：关闭脚本启动的两个新 PowerShell 窗口（或在窗口内按 Ctrl+C）。

## 手动启动（MySQL：严格按 SQL 初始化）

1) 初始化数据库（按顺序执行）

```sql
source database/schema.sql;
source database/init_data.sql;
-- 可选：source database/test_data.sql;
```

2) 配置后端连接（`backend/.env`，可复制 `backend/.env.example`）

```ini
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/community_hospital?charset=utf8mb4
JWT_SECRET_KEY=change-me
```

3) 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

4) 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 快速启动（SQLite：开发/演示用，非作业要求）

1) 启动后端（初始化表 + 种子数据）

```bash
cd backend
pip install -r requirements.txt
python run.py
```

默认启用 `AUTO_SEED=1`：启动时会自动创建表并填充演示数据（科室/诊室/员工/排班/默认账号），如需关闭可在 `backend/.env` 设置 `AUTO_SEED=0`。

2) 启动前端

```bash
cd frontend
npm install
npm run dev
```

3) 默认账号

- 管理员：`admin / admin123`
- 前台：`reception / reception123`
- 测试患者：`patient1 / patient123`（也可以从登录页进入“患者注册”自行注册）

前端默认通过 Vite 代理把 `/api` 转发到 `http://localhost:5000`（见 `frontend/vite.config.js`）。

## 账号与角色

- 管理员：`admin / admin123`（登录后进入“管理后台”）
- 前台：`reception / reception123`（登录后进入“前台工作台”）
- 测试患者：`patient1 / patient123`（也可以右上角“患者注册”自行注册后登录）

## 演示闭环（建议录屏脚本）

1) 患者端：注册/登录后进入 `预约挂号`，提交预约（得到 `appt_id`）
2) 前台端：登录前台账号进入 `预约处理`，对该预约点击 `到院签到`（生成 `visit_id`，分配诊室/医生）
3) 前台端：进入 `就诊/缴费` 将状态 `候诊中 → 就诊中 → 待缴费`
4) 前台端：对 `待缴费` 的 visit 进行 `缴费结算`，状态变为 `已离院` 并生成收入记录

## 功能入口（网页位置说明）

页面入口均在顶部菜单栏，且会根据登录角色自动显示/隐藏。

### 1) 患者端（patient）

- 入口：顶部菜单 `预约挂号`（`/patient/appointment`）
  - 在线预约：选择“就诊科室 + 预计到达时间”提交预约
  - 我的预约记录：按状态筛选、取消未完成预约

### 2) 前台端（receptionist）

入口：顶部菜单 `前台工作台`

- `挂号登记`（`/receptionist/register`）：现场登记就诊（录入患者信息并生成 `visit`，分配诊室/医生）
- `预约处理`（`/receptionist/appointments`）：预约确认/取消；到院核验后“到院签到”（预约转就诊）
- `就诊/缴费`（`/receptionist/visits`）
  - 状态流转：`候诊中 → 就诊中 → 待缴费`
  - 缴费结算：对“待缴费”的就诊点击 `缴费结算`，录入金额后完成支付并生成收入记录
- `患者信息`（`/receptionist/patients`）：按姓名/电话/身份证查询患者简略信息
- `收费报表`（`/receptionist/bills`）：按日期/科室/医生/患者信息等条件筛选账单并汇总本页金额

### 3) 管理员端（admin / 医务科）

入口：顶部菜单 `管理后台`

- `诊室管理`（`/admin/rooms`）：新增/编辑诊室（诊室号、所属科室、启停用）
- `排班管理`（`/admin/schedules`）：新增/编辑/删除医生排班（日期、时间段、诊室、容量等）
- `员工管理`（`/admin/employees`）：新增/编辑员工（医生/护士/前台/管理员）
- `统计报表`（`/admin/statistics`）：收入/就诊统计（按科室/医生/日期分组，支持日期范围）
- `账单查询`（`/admin/bills`）：全量账单筛选查询（含分页与本页合计）
- `收入明细`（`/admin/income-records`）：收入记录明细查询（含分页与本页合计）
- `患者查询`（`/admin/patients`）：患者信息查询
- `就诊查询`（`/admin/visits`）：就诊记录筛选查询；点击 `病历` 可查看/编辑该次就诊的病历信息

## 说明

- 系统通过登录账号区分角色：患者注册登录进入预约；前台账号进入挂号/预约/缴费；管理员账号进入排班与统计。
- 关键一致性点：就诊状态流转、预约转就诊、排班容量校验、缴费结算与收入记录（见 `PLAN.md`）。

## 常见问题

- “选择科室为空”：说明数据库里 `department` 没有数据。请优先用 `start.ps1` 初始化 MySQL，或在 SQLite 模式确保 `AUTO_SEED=1`。
- 登录后接口 401：请刷新页面重新登录；如仍异常，清空浏览器 LocalStorage 后再试（旧 token 可能已失效）。
