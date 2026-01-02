// API配置
const API_BASE_URL = '/api';

// 获取DOM元素
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const featureButtons = document.querySelectorAll('.feature-btn');

// 状态变量
let isProcessing = false;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 绑定事件监听器
    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // 绑定功能按钮事件
    featureButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.dataset.prompt;
            if (prompt) {
                userInput.value = prompt;
                handleSendMessage();
            }
        });
    });
    
    // 自动聚焦输入框
    userInput.focus();
});

// 处理发送消息
async function handleSendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }
    
    // 清空输入框
    userInput.value = '';
    
    // 显示用户消息
    addMessage(message, 'user');
    
    // 显示加载状态
    showLoading();
    
    try {
        // 调用API
        const response = await sendMessageToAgent(message);
        
        // 隐藏加载状态
        hideLoading();
        
        // 显示AI回复
        addMessage(response, 'bot');
    } catch (error) {
        hideLoading();
        addMessage(`抱歉，发生了错误：${error.message}`, 'bot');
        console.error('Error:', error);
    }
}

// 发送消息到Agent
async function sendMessageToAgent(message) {
    const payload = {
        type: 'query',
        session_id: generateSessionId(),
        message: message,
        content: {
            query: {
                prompt: [
                    {
                        type: 'text',
                        content: { text: message }
                    }
                ]
            }
        }
    };
    
    const response = await fetch(`${API_BASE_URL}/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.type === 'text' || data.type === 'tool_result') {
                        if (data.content && data.content.text) {
                            fullResponse += data.content.text;
                            // 实时更新最后一条消息（可选）
                        }
                    }
                } catch (e) {
                    console.error('Error parsing SSE data:', e);
                }
            }
        }
    }
    
    return fullResponse || '抱歉，没有收到响应。';
}

// 添加消息到聊天界面
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 处理内容（支持简单的Markdown格式）
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    scrollToBottom();
}

// 格式化消息（简单Markdown支持）
function formatMessage(text) {
    if (!text) return '';
    
    // 转义HTML
    let formatted = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 处理换行
    formatted = formatted.replace(/\n/g, '<br>');
    
    // 处理粗体 **text**
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // 处理斜体 *text*
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // 处理链接 [text](url)
    formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    
    // 处理图片 ![alt](url)
    formatted = formatted.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">');
    
    // 处理代码 `text`
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 处理代码块
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    
    return formatted;
}

// 显示加载状态
function showLoading() {
    isProcessing = true;
    sendButton.disabled = true;
    sendButton.innerHTML = '<span class="loading">AI思考中</span>';
}

// 隐藏加载状态
function hideLoading() {
    isProcessing = false;
    sendButton.disabled = false;
    sendButton.innerHTML = '发送';
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 生成会话ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}
