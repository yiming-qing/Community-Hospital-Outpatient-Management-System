# 社区医院门诊管理系统 - 实现计划

## 项目概述
为中山大学数据库系统实验大作业开发一个完整的社区医院门诊管理系统。

### 项目信息
- **项目名称**: `community-hospital-system`
- **开发范围**: 完整版（所有要求功能 + 美观UI + ECharts图表统计）

### 技术栈
- **后端**: Python Flask + SQLAlchemy
- **数据库**: MySQL 8.0
- **前端**: Vue.js 3 + Element Plus
- **认证**: JWT (Flask-JWT-Extended)

### 用户角色
1. 患者 - 预约挂号、查询预约
2. 前台 - 登记就诊、签到、缴费结算
3. 管理员 - 排班管理、统计查询、员工管理

---

## 与《实验考察1.pdf》要求对照（Checklist）

- 参考数据库：社区医院门诊管理系统（患者 / 前台 / 管理人员三类角色）
- 核心流程：预约 → 到院登记/签到 → 就诊 → 缴费离院（视频需演示）
- 管理功能：排班/诊室维护；账单与收入统计（按日期/科室/医生）；患者与员工信息查询/修改
- 数据一致性：外键、唯一性、状态流转约束、排班容量约束；关键写操作使用事务
- 交付物：GitHub 代码仓库、演示视频链接、实验报告、PPT（pdf 中写的最终提交时间为 1 月 15 日，以课程通知为准）

---

## 一、数据库设计

### 1.1 实体关系图（核心实体）

```
患者(Patient) ──< 预约(Appointment) >── 科室(Department)
     │                                        │
     │                                        │
     └────────< 就诊(Visit) >─────────── 诊室(Room)
                    │                         │
                    │                         │
               账单(Bill)              排班(Schedule) >── 员工(Employee)
                    │                                        │
              收入记录(Income)                         系统账号(SysUser)
```

### 1.2 数据表设计

```sql
-- 1. 科室表
CREATE TABLE department (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 员工表
CREATE TABLE employee (
    emp_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    phone VARCHAR(20),
    position ENUM('医生', '护士', '前台', '管理员') NOT NULL,
    title VARCHAR(50),
    dept_id INT,
    status ENUM('在职', '离职', '休假') DEFAULT '在职',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- 3. 系统账号表（避免与 MySQL 内置 mysql.user 混淆，命名为 sys_user）
CREATE TABLE sys_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_id VARCHAR(20),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'receptionist', 'admin') NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
);

-- 4. 诊室表
CREATE TABLE room (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(20) NOT NULL UNIQUE,
    dept_id INT NOT NULL,
    status ENUM('启用', '停用') DEFAULT '启用',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

-- 5. 排班表
CREATE TABLE schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    room_id INT NOT NULL,
    doctor_id VARCHAR(20) NOT NULL,
    work_date DATE NOT NULL,
    time_slot ENUM('上午', '下午', '全天') NOT NULL,
    max_patients INT DEFAULT 30,
    current_patients INT DEFAULT 0,
    FOREIGN KEY (room_id) REFERENCES room(room_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
    UNIQUE KEY (room_id, work_date, time_slot)
);

-- 6. 患者表
CREATE TABLE patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    gender ENUM('男', '女'),
    id_card VARCHAR(18) UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_id_card (id_card)
);

-- 7. 预约表
CREATE TABLE appointment (
    appt_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    dept_id INT NOT NULL,
    expected_time DATETIME NOT NULL,
    status ENUM('待确认', '已确认', '已完成', '已取消') DEFAULT '待确认',
    patient_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
);

-- 8. 就诊记录表
CREATE TABLE visit (
    visit_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    room_id INT NOT NULL,
    doctor_id VARCHAR(20),
    appt_id INT,
    status ENUM('候诊中', '就诊中', '待缴费', '已离院') DEFAULT '候诊中',
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checkout_time TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (room_id) REFERENCES room(room_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
    FOREIGN KEY (appt_id) REFERENCES appointment(appt_id),
    UNIQUE KEY uniq_visit_appt (appt_id)
);

-- 9. 账单表
CREATE TABLE bill (
    bill_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL UNIQUE,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    insurance_amount DECIMAL(10,2) DEFAULT 0,
    self_pay_amount DECIMAL(10,2) DEFAULT 0,
    pay_status ENUM('未支付', '已支付') DEFAULT '未支付',
    pay_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id)
);

-- 10. 收入记录表
CREATE TABLE income_record (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_id INT NOT NULL,
    dept_id INT NOT NULL,
    doctor_id VARCHAR(20),
    amount DECIMAL(10,2) NOT NULL,
    record_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bill_id) REFERENCES bill(bill_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id)
);
```

### 1.3 数据一致性与完整性（建议写进报告/答辩）

- 外键与唯一性：科室/诊室/排班/就诊/账单/收入记录的外键与唯一键（如 `visit.appt_id` 唯一、`bill.visit_id` 唯一）
- 状态流转约束：预约（待确认→已确认→已完成/已取消），就诊（候诊中→就诊中→待缴费→已离院），避免越级与回退
- 排班容量约束：创建就诊/签到时校验 `current_patients < max_patients`，并在同一事务内递增
- 金额一致性：账单金额字段满足 `total_amount = insurance_amount + self_pay_amount`，支付时写入 `pay_time` 并生成收入记录
- 关键写操作事务：预约签到（更新预约 + 创建就诊 + 更新排班）、缴费结算（更新账单 + 更新就诊状态 + 记录收入）

---

## 二、项目结构

```
community-hospital-system/
├── backend/                      # Flask 后端
│   ├── app/
│   │   ├── __init__.py          # 应用工厂
│   │   ├── config.py            # 配置
│   │   ├── extensions.py        # 扩展
│   │   ├── models/              # 数据模型
│   │   ├── api/                 # API 路由
│   │   ├── services/            # 业务逻辑
│   │   └── utils/               # 工具函数
│   ├── requirements.txt
│   └── run.py
├── frontend/                     # Vue 前端
│   ├── src/
│   │   ├── api/                 # API 封装
│   │   ├── views/               # 页面
│   │   ├── components/          # 组件
│   │   ├── router/              # 路由
│   │   └── store/               # 状态管理
│   └── package.json
├── database/                     # SQL 脚本
│   ├── schema.sql
│   ├── init_data.sql
│   └── test_data.sql
└── README.md
```

---

## 三、API 接口设计

### 3.1 认证 `/api/auth`
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /login | 登录 |
| POST | /logout | 登出 |
| GET | /profile | 获取用户信息 |

### 3.2 患者端 `/api/patient`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /departments | 获取科室列表 |
| POST | /appointment | 创建预约 |
| GET | /appointment/query | 查询预约 |
| DELETE | /appointment/:id | 取消预约 |

### 3.3 前台 `/api/receptionist`
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /register | 现场登记 |
| GET | /appointments | 预约列表 |
| POST | /checkin/:appt_id | 预约签到 |
| GET | /visits | 就诊列表 |
| PUT | /visit/:id/status | 更新就诊状态 |
| POST | /payment/:visit_id | 缴费结算 |
| GET | /patients | 患者列表 |

### 3.4 管理员 `/api/admin`
| 方法 | 路径 | 描述 |
|------|------|------|
| GET/POST/PUT | /rooms | 诊室管理 |
| GET/POST/PUT/DELETE | /schedules | 排班管理 |
| GET | /statistics/income | 收入统计 |
| GET | /statistics/visits | 就诊统计 |
| GET | /patients/search | 患者查询 |
| GET/PUT/POST | /employees | 员工管理 |

---

## 四、实现步骤

### 阶段1: 基础搭建
- [ ] 初始化 Flask 项目结构
- [ ] 初始化 Vue.js 项目
- [ ] 配置数据库连接
- [ ] 执行建表 SQL
- [ ] 插入初始数据（科室、管理员账号）

### 阶段2: 认证系统
- [ ] 实现用户登录/登出 API
- [ ] JWT 令牌认证
- [ ] 登录页面
- [ ] 路由权限控制

### 阶段3: 患者端功能
- [ ] 科室列表 API
- [ ] 预约创建 API
- [ ] 预约查询 API
- [ ] 预约页面

### 阶段4: 前台功能
- [ ] 现场登记 API 和页面
- [ ] 预约签到 API 和页面
- [ ] 就诊状态管理
- [ ] 缴费结算 API 和页面
- [ ] 患者列表页面

### 阶段5: 管理功能
- [ ] 诊室管理
- [ ] 排班管理
- [ ] 收入统计和图表
- [ ] 患者详细查询
- [ ] 员工管理

### 阶段6: 测试与优化
- [ ] 功能测试
- [ ] Bug 修复
- [ ] UI 优化

### 阶段7: 文档与提交
- [ ] 实验报告
- [ ] PPT 制作
- [ ] 演示视频
- [ ] GitHub 提交

---

## 五、核心业务流程

### 预约流程
```
患者填写预约 → 创建预约(待确认) → 到院签到 → 核验身份
→ 创建就诊记录 → 预约标记已完成
```

### 现场登记流程
```
前台录入患者信息 → 创建患者记录 → 分配诊室 → 创建就诊记录(候诊中)
```

### 缴费离院流程
```
就诊完成 → 状态变为待缴费 → 生成账单 → 前台收费
→ 账单已支付 → 就诊状态已离院
```

---

## 六、关键文件清单

### 后端
- `backend/app/__init__.py` - Flask 应用初始化
- `backend/app/config.py` - 数据库配置
- `backend/app/models/*.py` - 数据模型
- `backend/app/api/auth.py` - 认证 API
- `backend/app/api/receptionist.py` - 前台 API（核心）
- `backend/app/api/admin.py` - 管理员 API
- `backend/app/services/statistics_service.py` - 统计服务

### 前端
- `frontend/src/router/index.js` - 路由配置
- `frontend/src/api/*.js` - API 请求
- `frontend/src/views/Login.vue` - 登录页
- `frontend/src/views/receptionist/Registration.vue` - 登记页
- `frontend/src/views/receptionist/Payment.vue` - 缴费页
- `frontend/src/views/admin/Schedule.vue` - 排班管理
- `frontend/src/views/admin/Statistics.vue` - 统计页

### 数据库
- `database/schema.sql` - 建表脚本
- `database/init_data.sql` - 初始化数据
- `database/test_data.sql` - 测试数据

---

## 七、团队分工建议（3-4人）

| 成员 | 负责模块 | 具体内容 |
|------|----------|----------|
| 成员 A | 后端/数据库 | 表结构与约束、核心 API、事务与一致性、统计查询 SQL |
| 成员 B | 前端 | 页面与交互、权限路由、ECharts 图表、联调与体验优化 |
| 成员 C | 全栈/测试/文档 | 测试数据与用例、接口联调、实验报告与 PPT、演示脚本与录屏 |
| （可选）成员 D | 运维/工程化 | 部署脚本、环境文档、CI/格式化、容器化（如需） |

---

## 八、交付物

1. **GitHub 代码仓库** - 包含完整源代码
2. **功能演示视频** - 演示预约→登记→就诊→缴费流程
3. **实验报告** - 需求分析、数据库设计、功能实现、测试用例
4. **PPT** - 项目背景、设计、演示、创新点
