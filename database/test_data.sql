-- 社区医院门诊管理系统 - 测试数据（可选）
USE community_hospital;

-- 1) 创建一个患者
INSERT INTO patient (patient_id, name, gender, id_card, phone) VALUES
  (1, '测试患者', '男', '440101199001011234', '13900000000')
ON DUPLICATE KEY UPDATE phone = VALUES(phone);

-- 2) 创建一个“今天上午”的预约（默认待确认）
INSERT INTO appointment (appt_id, patient_name, phone, dept_id, expected_time, status, patient_id) VALUES
  (1, '测试患者', '13900000000', 1, CONCAT(CURDATE(), ' 09:30:00'), '待确认', 1)
ON DUPLICATE KEY UPDATE expected_time = VALUES(expected_time);

