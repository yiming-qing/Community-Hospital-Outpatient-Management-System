-- 社区医院门诊管理系统 - 数据库建表脚本（MySQL 8.0）
-- 字符集建议使用 utf8mb4，存储中文枚举值与姓名等信息。

CREATE DATABASE IF NOT EXISTS community_hospital
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE community_hospital;

-- 1. 科室表
CREATE TABLE IF NOT EXISTS department (
  dept_id INT PRIMARY KEY AUTO_INCREMENT,
  dept_name VARCHAR(50) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 员工表
CREATE TABLE IF NOT EXISTS employee (
  emp_id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  gender ENUM('男', '女') NOT NULL,
  phone VARCHAR(20),
  position ENUM('医生', '护士', '前台', '管理员') NOT NULL,
  title VARCHAR(50),
  dept_id INT,
  status ENUM('在职', '离职', '休假') NOT NULL DEFAULT '在职',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_employee_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 系统账号表（命名为 sys_user，避免与 mysql.user 混淆）
CREATE TABLE IF NOT EXISTS sys_user (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  emp_id VARCHAR(20),
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('patient', 'receptionist', 'admin') NOT NULL,
  status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
  last_login TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_user_employee FOREIGN KEY (emp_id) REFERENCES employee(emp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 诊室表
CREATE TABLE IF NOT EXISTS room (
  room_id INT PRIMARY KEY AUTO_INCREMENT,
  room_number VARCHAR(20) NOT NULL UNIQUE,
  dept_id INT NOT NULL,
  status ENUM('启用', '停用') NOT NULL DEFAULT '启用',
  CONSTRAINT fk_room_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 排班表
CREATE TABLE IF NOT EXISTS schedule (
  schedule_id INT PRIMARY KEY AUTO_INCREMENT,
  room_id INT NOT NULL,
  doctor_id VARCHAR(20) NOT NULL,
  work_date DATE NOT NULL,
  time_slot ENUM('上午', '下午', '全天') NOT NULL,
  max_patients INT NOT NULL DEFAULT 30,
  current_patients INT NOT NULL DEFAULT 0,
  CONSTRAINT ck_schedule_capacity CHECK (current_patients <= max_patients),
  CONSTRAINT fk_schedule_room FOREIGN KEY (room_id) REFERENCES room(room_id),
  CONSTRAINT fk_schedule_doctor FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
  UNIQUE KEY uniq_room_date_slot (room_id, work_date, time_slot),
  INDEX idx_schedule_work_date (work_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 患者表
CREATE TABLE IF NOT EXISTS patient (
  patient_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  gender ENUM('男', '女'),
  id_card VARCHAR(18) UNIQUE,
  phone VARCHAR(20) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_patient_phone (phone),
  INDEX idx_patient_id_card (id_card)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6.1 患者账号映射表（sys_user.role='patient' 时使用）
CREATE TABLE IF NOT EXISTS patient_user (
  user_id INT PRIMARY KEY,
  patient_id INT NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_patient_user_user FOREIGN KEY (user_id) REFERENCES sys_user(user_id) ON DELETE CASCADE,
  CONSTRAINT fk_patient_user_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 预约表
CREATE TABLE IF NOT EXISTS appointment (
  appt_id INT PRIMARY KEY AUTO_INCREMENT,
  patient_name VARCHAR(50) NOT NULL,
  phone VARCHAR(20) NOT NULL,
  dept_id INT NOT NULL,
  expected_time DATETIME NOT NULL,
  status ENUM('待确认', '已确认', '已完成', '已取消') NOT NULL DEFAULT '待确认',
  patient_id INT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_appt_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id),
  CONSTRAINT fk_appt_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
  INDEX idx_appt_phone (phone),
  INDEX idx_appt_expected_time (expected_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. 就诊记录表
CREATE TABLE IF NOT EXISTS visit (
  visit_id INT PRIMARY KEY AUTO_INCREMENT,
  patient_id INT NOT NULL,
  room_id INT NOT NULL,
  doctor_id VARCHAR(20),
  appt_id INT,
  status ENUM('候诊中', '就诊中', '待缴费', '已离院') NOT NULL DEFAULT '候诊中',
  check_in_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  checkout_time TIMESTAMP NULL,
  CONSTRAINT fk_visit_patient FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
  CONSTRAINT fk_visit_room FOREIGN KEY (room_id) REFERENCES room(room_id),
  CONSTRAINT fk_visit_doctor FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
  CONSTRAINT fk_visit_appt FOREIGN KEY (appt_id) REFERENCES appointment(appt_id),
  UNIQUE KEY uniq_visit_appt (appt_id),
  INDEX idx_visit_status (status),
  INDEX idx_visit_check_in_time (check_in_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. 账单表
CREATE TABLE IF NOT EXISTS bill (
  bill_id INT PRIMARY KEY AUTO_INCREMENT,
  visit_id INT NOT NULL UNIQUE,
  total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  insurance_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  self_pay_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  pay_status ENUM('未支付', '已支付') NOT NULL DEFAULT '未支付',
  pay_time TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT ck_bill_amount CHECK (total_amount = insurance_amount + self_pay_amount),
  CONSTRAINT fk_bill_visit FOREIGN KEY (visit_id) REFERENCES visit(visit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. 收入记录表
CREATE TABLE IF NOT EXISTS income_record (
  record_id INT PRIMARY KEY AUTO_INCREMENT,
  bill_id INT NOT NULL,
  dept_id INT NOT NULL,
  doctor_id VARCHAR(20),
  amount DECIMAL(10,2) NOT NULL,
  record_date DATE NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_income_bill FOREIGN KEY (bill_id) REFERENCES bill(bill_id),
  CONSTRAINT fk_income_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id),
  CONSTRAINT fk_income_doctor FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
  INDEX idx_income_record_date (record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. 病历表（每次就诊对应一份病历，可由管理员维护）
CREATE TABLE IF NOT EXISTS medical_record (
  record_id INT PRIMARY KEY AUTO_INCREMENT,
  visit_id INT NOT NULL UNIQUE,
  diagnosis TEXT,
  treatment TEXT,
  prescription TEXT,
  note TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_medical_record_visit FOREIGN KEY (visit_id) REFERENCES visit(visit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
