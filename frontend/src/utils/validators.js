// frontend/src/utils/validators.js

// 中国大陆手机号：11位，以1开头，第二位3-9
export const CN_MOBILE_PATTERN = /^1[3-9]\d{9}$/;

// Element Plus 表单规则：手机号
export const phoneRules = [
  { required: true, message: '请输入电话号码', trigger: 'blur' },
  { pattern: CN_MOBILE_PATTERN, message: '请输入合法的11位手机号', trigger: 'blur' }
];
