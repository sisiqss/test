/**
 * 前端调用后端 API 示例
 *
 * 注意：前端应该调用 localhost:5000，而不是 Coze API
 */

// 配置
const API_BASE_URL = 'http://localhost:5000';

/**
 * 调用后端 API 的通用函数
 */
async function callBackendAPI(endpoint, data = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok || result.status === 'failed') {
      throw new Error(result.error_message || 'API 调用失败');
    }

    return result;
  } catch (error) {
    console.error('API 调用失败:', error);
    throw error;
  }
}

/**
 * 示例 1: 用户登录
 */
async function login(username, password) {
  console.log('🔐 正在登录...');

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'login',
    tool_params: {
      username: username,
      password: password
    },
    user_id: username,  // 临时使用用户名作为 user_id
    message: '登录'
  });

  console.log('✅ 登录成功:', result.data);
  return result.data;
}

/**
 * 示例 2: 查询用户信息
 */
async function queryUser(userId) {
  console.log('🔍 正在查询用户信息...');

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'query_user_by_id',
    tool_params: {
      user_id: userId
    },
    user_id: userId,
    message: '查询用户信息'
  });

  console.log('✅ 查询成功:', result.data);
  return result.data;
}

/**
 * 示例 3: 添加联系人
 */
async function addContact(userId, contactData) {
  console.log('👥 正在添加联系人...');

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'add_contact',
    tool_params: {
      user_id: userId,
      contact_data: JSON.stringify(contactData)
    },
    user_id: userId,
    message: '添加联系人'
  });

  console.log('✅ 添加成功:', result.data);
  return result.data;
}

/**
 * 示例 4: 查询联系人列表
 */
async function queryContacts(userId, contactType = null) {
  console.log('👥 正在查询联系人列表...');

  const params = {
    user_id: userId
  };

  if (contactType) {
    params.contact_type = contactType;
  }

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'query_contacts',
    tool_params: params,
    user_id: userId,
    message: '查询联系人列表'
  });

  console.log('✅ 查询成功:', result.data);
  return result.data;
}

/**
 * 示例 5: 获取每日运势和穿搭（推荐使用）
 */
async function getDailyFortuneAndOutfit(userId, reportDate = null) {
  console.log('🌟 正在获取每日运势和穿搭...');

  const params = {
    user_id: userId
  };

  if (reportDate) {
    params.report_date = reportDate;
  }

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'get_daily_fortune_and_outfit',
    tool_params: params,
    user_id: userId,
    message: '获取每日运势和穿搭'
  });

  console.log('✅ 获取成功:', result.data);
  return result.data;
}

/**
 * 示例 6: 获取消耗统计
 */
async function getUsageStatistics(userId, date = null) {
  console.log('📊 正在获取消耗统计...');

  const params = {
    admin_user_id: userId
  };

  if (date) {
    params.date_str = date;
  }

  const result = await callBackendAPI('/api/agent/chat', {
    tool_name: 'get_usage_statistics',
    tool_params: params,
    user_id: userId,
    message: '获取消耗统计'
  });

  console.log('✅ 获取成功:', result.data);
  return result.data;
}

/**
 * 示例 7: 普通对话（让 Agent 自动选择工具）
 */
async function chatWithAgent(userId, message) {
  console.log(`💬 发送消息: ${message}...`);

  const result = await callBackendAPI('/api/agent/chat', {
    message: message,
    user_id: userId,
    // 不指定 tool_name，让 Agent 自动选择工具
  });

  console.log('✅ 响应成功:', result.data);
  return result.data;
}

/**
 * 示例 8: 获取工具列表
 */
async function getToolsList() {
  console.log('🛠️ 正在获取工具列表...');

  const response = await fetch(`${API_BASE_URL}/api/tools`, {
    method: 'GET'
  });

  const result = await response.json();

  if (result.status === 'success') {
    console.log(`✅ 找到 ${result.total} 个工具:`);
    result.tools.forEach(tool => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });
  }

  return result;
}

/**
 * 测试函数
 */
async function runTests() {
  try {
    console.log('='.repeat(60));
    console.log('🧪 开始测试后端 API');
    console.log('='.repeat(60));

    // 1. 测试登录
    console.log('\n[测试 1] 登录');
    await login('admin', 'admin');

    // 2. 测试查询用户信息
    console.log('\n[测试 2] 查询用户信息');
    await queryUser('admin');

    // 3. 测试添加联系人
    console.log('\n[测试 3] 添加联系人');
    await addContact('admin', {
      name: '测试用户',
      gender: '男',
      relationship_type: 'colleague',
      current_location: '北京'
    });

    // 4. 测试查询联系人列表
    console.log('\n[测试 4] 查询联系人列表');
    await queryContacts('admin');

    // 5. 测试获取每日运势和穿搭
    console.log('\n[测试 5] 获取每日运势和穿搭');
    await getDailyFortuneAndOutfit('admin', '2025-01-03');

    // 6. 测试普通对话
    console.log('\n[测试 6] 普通对话');
    await chatWithAgent('admin', '你好，帮我查看人生解读');

    console.log('\n' + '='.repeat(60));
    console.log('✅ 所有测试通过！');
    console.log('='.repeat(60));

  } catch (error) {
    console.error('\n❌ 测试失败:', error);
  }
}

// 导出函数
export {
  login,
  queryUser,
  addContact,
  queryContacts,
  getDailyFortuneAndOutfit,
  getUsageStatistics,
  chatWithAgent,
  getToolsList,
  runTests
};

// 如果直接运行，执行测试
if (typeof window === 'undefined') {
  runTests();
}
