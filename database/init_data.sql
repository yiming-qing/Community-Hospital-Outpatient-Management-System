-- 社区医院门诊管理系统 - 初始化数据（MySQL 8.0）
USE community_hospital;

-- 科室
INSERT INTO department (dept_id, dept_name, description) VALUES
  (1, '内科', '常见内科疾病诊疗'),
  (2, '外科', '常见外科疾病诊疗'),
  (3, '口腔科', '口腔检查与治疗'),
  (4, '儿科', '儿童常见病诊疗')
ON DUPLICATE KEY UPDATE dept_name = VALUES(dept_name);

-- 诊室
INSERT INTO room (room_id, room_number, dept_id, status) VALUES
  (1, '101', 1, '启用'),
  (2, '102', 1, '启用'),
  (3, '201', 2, '启用'),
  (4, '301', 3, '启用'),
  (5, '401', 4, '启用')
ON DUPLICATE KEY UPDATE room_number = VALUES(room_number);

-- 员工（医生/前台/管理员）
INSERT INTO employee (emp_id, name, gender, phone, position, title, dept_id, status) VALUES
  ('D001', '李医生', '男', '13800000001', '医生', '主治医师', 1, '在职'),
  ('D002', '王医生', '女', '13800000002', '医生', '主治医师', 2, '在职'),
  ('D003', '张医生', '男', '13800000003', '医生', '主治医师', 3, '在职'),
  ('R001', '前台小赵', '女', '13800000011', '前台', NULL, 1, '在职'),
  ('A001', '管理员小陈', '男', '13800000021', '管理员', NULL, NULL, '在职')
ON DUPLICATE KEY UPDATE name = VALUES(name);

-- 系统账号（默认密码：admin123 / reception123）
-- password_hash 由 Werkzeug generate_password_hash 生成（scrypt），可在上线前自行更换。
INSERT INTO sys_user (user_id, emp_id, username, password_hash, role, status) VALUES
  (1, 'A001', 'admin', 'scrypt:32768:8:1$1FYnCnwbNvqeqE5M$c1d6cd2c07e7cc474b14026e2aa335e2ad5906e4438f552572d43571dbc6ef58fd30dbdaad26d9297400e140ccdcfc74edbc791e4c25b2c5ce6e130c6b2174bd', 'admin', 'active'),
  (2, 'R001', 'reception', 'scrypt:32768:8:1$fkZu3EGRVGPLiSJZ$4a7922e886fc91c48157bb9bd48f9cc6fc257e0afefcf21244e4a7c51ebee6e29bb2d6456868c68918de764307690b880504bdfa5bb9ae5aae1d29914ab60530', 'receptionist', 'active')
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- 排班（使用 CURDATE() 生成“今天/明天”的样例排班）
-- 注意：为简化示例，这里只给每个科室安排一名医生；实际可按需求扩展。
INSERT INTO schedule (room_id, doctor_id, work_date, time_slot, max_patients, current_patients) VALUES
  (1, 'D001', CURDATE(), '上午', 30, 0),
  (1, 'D001', CURDATE(), '下午', 30, 0),
  (3, 'D002', CURDATE(), '上午', 30, 0),
  (3, 'D002', CURDATE(), '下午', 30, 0),
  (4, 'D003', CURDATE(), '上午', 30, 0),
  (4, 'D003', CURDATE(), '下午', 30, 0),

  (1, 'D001', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '上午', 30, 0),
  (1, 'D001', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '下午', 30, 0),
  (3, 'D002', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '上午', 30, 0),
  (3, 'D002', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '下午', 30, 0),
  (4, 'D003', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '上午', 30, 0),
  (4, 'D003', DATE_ADD(CURDATE(), INTERVAL 1 DAY), '下午', 30, 0)
ON DUPLICATE KEY UPDATE max_patients = VALUES(max_patients);

