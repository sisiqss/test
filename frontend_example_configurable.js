/**
 * 前端调用示例 - 支持配置 API Base URL
 */

// ====================================
// 配置 API Base URL
// ====================================
// 方式1：硬编码（不推荐）
// const API_BASE_URL = 'https://your-domain.com';

// 方式2：从环境变量读取（推荐）
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

// 方式3：从配置文件读取
// const API_BASE_URL = require('./config.js').API_BASE_URL;

console.log(`API Base URL: ${API_BASE_URL}`);

// ====================================
// API 调用函数
// ====================================

/**
 * 调用 Agent 工具
 */
async function callAgentTool(toolName, toolParams, userId) {
    const url = `${API_BASE_URL}/api/agent/chat`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tool_name: toolName,
                tool_params: toolParams,
                user_id: userId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.status === 'success') {
            return result.data;
        } else {
            throw new Error(result.error_message || '工具调用失败');
        }
    } catch (error) {
        console.error('调用失败:', error);
        throw error;
    }
}

/**
 * 发送消息给 Agent
 */
async function sendMessage(message, userId) {
    const url = `${API_BASE_URL}/api/agent/chat`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                user_id: userId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.status === 'success') {
            return result.data;
        } else {
            throw new Error(result.error_message || '消息发送失败');
        }
    } catch (error) {
        console.error('发送失败:', error);
        throw error;
    }
}

/**
 * 健康检查
 */
async function healthCheck() {
    const url = `${API_BASE_URL}/api/health`;

    try {
        const response = await fetch(url);
        const result = await response.json();

        if (result.status === 'ok') {
            console.log('✅ 服务健康', result);
            return result;
        } else {
            console.warn('⚠️ 服务异常', result);
            return result;
        }
    } catch (error) {
        console.error('健康检查失败:', error);
        throw error;
    }
}

/**
 * 获取工具列表
 */
async function getTools() {
    const url = `${API_BASE_URL}/api/tools`;

    try {
        const response = await fetch(url);
        const result = await response.json();

        if (result.status === 'success') {
            console.log(`📋 可用工具 (${result.total}个):`, result.tools);
            return result.tools;
        } else {
            throw new Error(result.error_message || '获取工具列表失败');
        }
    } catch (error) {
        console.error('获取工具列表失败:', error);
        throw error;
    }
}

// ====================================
// 使用示例
// ====================================

// 示例1：登录
async function exampleLogin() {
    try {
        const result = await callAgentTool('login', {
            username: 'admin',
            password: 'admin'
        }, 'admin');

        console.log('登录成功:', result);
        return result;
    } catch (error) {
        console.error('登录失败:', error);
    }
}

// 示例2：查询用户信息
async function exampleGetUserInfo() {
    try {
        const result = await callAgentTool('get_user_info', {}, 'admin');
        console.log('用户信息:', result);
        return result;
    } catch (error) {
        console.error('查询失败:', error);
    }
}

// 示例3：查询联系人列表
async function exampleGetContacts() {
    try {
        const result = await callAgentTool('query_contacts', {}, 'admin');
        console.log('联系人列表:', result);
        return result;
    } catch (error) {
        console.error('查询失败:', error);
    }
}

// 示例4：发送聊天消息
async function exampleChat() {
    try {
        const result = await sendMessage('你好，我想查看今天的运势', 'admin');
        console.log('Agent回复:', result);
        return result;
    } catch (error) {
        console.error('聊天失败:', error);
    }
}

// ====================================
// 执行示例
// ====================================

(async () => {
    console.log('='.repeat(60));
    console.log('  前端调用示例');
    console.log('='.repeat(60));

    // 健康检查
    await healthCheck();

    // 获取工具列表
    await getTools();

    // 示例：登录
    await exampleLogin();

    // 示例：查询用户信息
    await exampleGetUserInfo();

    // 示例：查询联系人
    await exampleGetContacts();

    // 示例：聊天
    await exampleChat();

    console.log('='.repeat(60));
    console.log('  示例执行完成');
    console.log('='.repeat(60));
})();
