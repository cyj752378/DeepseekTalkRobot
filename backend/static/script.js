// 后端 API 地址（FastAPI 服务地址）
const API_URL = "http://localhost:8000/api/chat";

// DOM 元素
const chatMessagesEl = document.getElementById("chatMessages");
const userInputEl = document.getElementById("userInput");
const sendBtnEl = document.getElementById("sendBtn");

// 初始化页面
function init() {
    // 添加欢迎消息
    addMessage("助手", "你好！我是基于 DeepSeek 的对话助手，有什么可以帮你的？", "assistant");

    // 绑定事件
    sendBtnEl.addEventListener("click", sendMessage);
    userInputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// 发送消息
async function sendMessage() {
    const message = userInputEl.value.trim();
    if (!message) return;

    // 清空输入框并禁用发送按钮
    userInputEl.value = "";
    sendBtnEl.disabled = true;

    // 添加用户消息到界面
    addMessage("你", message, "user");

    try {
        // 调用后端 API
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message: message,
                // 可自定义系统提示词
                system_prompt: "你是一个友好、专业的助手，用简洁明了的语言回答用户问题。",
                temperature: 0.7
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP 错误！状态码: ${response.status}`);
        }

        const data = await response.json();

        // 添加助手回复到界面
        addMessage("助手", data.response, "assistant");

    } catch (error) {
        console.error("发送消息失败:", error);
        addMessage("系统", "抱歉，请求失败，请稍后再试～", "assistant");
    } finally {
        // 启用发送按钮
        sendBtnEl.disabled = false;
        // 滚动到最新消息
        scrollToBottom();
    }
}

// 添加消息到聊天界面
function addMessage(sender, content, role) {
    const messageEl = document.createElement("div");
    messageEl.className = `chat-message ${role === "user" ? "user-message" : "assistant-message"}`;

    // 构建消息内容（支持换行）
    const formattedContent = content.replace(/\n/g, "<br>");
    messageEl.innerHTML = `<strong>${sender}:</strong> ${formattedContent}`;

    chatMessagesEl.appendChild(messageEl);
    scrollToBottom();
}

// 滚动到最新消息
function scrollToBottom() {
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

// 初始化应用
init();