// Check for maintenance mode from data attribute
const mainContainer = document.getElementById('main-container');
const maintenanceMode = mainContainer.getAttribute('data-maintenance') === "true";
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

if (maintenanceMode) {
    mainContainer.classList.add('maintenance-mode');
    
    // Add system message explaining maintenance mode
    const chatBox = document.getElementById('chat-box');
    const systemMsg = document.createElement('div');
    systemMsg.className = 'message system';
    systemMsg.innerHTML = `
        <div class="system-avatar"><i class="fas fa-wrench"></i></div>
        <div class="message-content">
            The system is currently in maintenance mode. You can still ask questions, 
            but some functionalities may be limited. We apologize for any inconvenience.
        </div>
    `;
    chatBox.appendChild(systemMsg);
}

// Event listener for the send button and Enter key
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Function to simulate typing effect (without cursor)
function typeEffect(element, text, speed = 30) {
    let i = 0;
    element.innerHTML = '';
    
    function typing() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            element.scrollIntoView({ behavior: "smooth", block: "end" });
            setTimeout(typing, speed);
        }
    }
    
    typing();
}

function sendMessage() {
    const inputElem = document.getElementById('user-input');
    const question = inputElem.value.trim();
    if (!question) return;
    
    const chatBox = document.getElementById('chat-box');
    
    // Append user's message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = `<div class="message-content">${question}</div>`;
    chatBox.appendChild(userMsg);
    
    inputElem.value = "";  // Clear input field
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    
    // Disable input during processing
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot';
    typingIndicator.innerHTML = `
        <div class="bot-avatar">MD</div>
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // Send question to backend
    fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Network response error: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Remove typing indicator
        chatBox.removeChild(typingIndicator);
        
        // Create bot's response container
        const botMsg = document.createElement('div');
        botMsg.className = 'message bot';
        botMsg.innerHTML = `
            <div class="bot-avatar">MD</div>
            <div class="message-content"></div>
        `;
        chatBox.appendChild(botMsg);
        
        // Get the message content element
        const messageContent = botMsg.querySelector('.message-content');
        
        // Check if system is in maintenance mode (from response)
        if (data.maintenance_mode) {
            botMsg.classList.add('system');
            botMsg.querySelector('.bot-avatar').classList.replace('bot-avatar', 'system-avatar');
            botMsg.querySelector('.system-avatar').innerHTML = '<i class="fas fa-wrench"></i>';
        }
        
        // Apply typing effect to the bot's response using the new 'response' field
        typeEffect(messageContent, data.response || "I'm sorry, I couldn't process your request properly.");
        
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
        
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    })
    .catch(error => {
        // Remove typing indicator
        chatBox.removeChild(typingIndicator);
        
        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'message system';
        const errorContent = document.createElement('div');
        errorContent.className = 'message-content';
        
        // Append to DOM
        errorMsg.innerHTML = `<div class="system-avatar"><i class="fas fa-exclamation-triangle"></i></div>`;
        errorMsg.appendChild(errorContent);
        chatBox.appendChild(errorMsg);
        
        // Apply typing effect to error message
        typeEffect(errorContent, "Sorry, there was an error processing your request. Please try again.");
        
        chatBox.scrollTop = chatBox.scrollHeight;
        console.error("Error:", error);
        
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    });
}

// Simulate real-time typing for the initial message
window.addEventListener('load', function() {
    const initialMessage = document.querySelector('.message.bot .message-content');
    const initialText = initialMessage.textContent.trim();
    initialMessage.textContent = '';
    setTimeout(() => {
        typeEffect(initialMessage, initialText);
    }, 500);
});

// Function to generate a random hex color
function getRandomColor() {
    return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}

// Event listener for the brush (color) button
document.getElementById('color-button').addEventListener('click', function() {
    const randomColor = getRandomColor();
    // Update primary color variables to change the chatbot's theme
    document.documentElement.style.setProperty('--primary-color', randomColor);
    document.documentElement.style.setProperty('--user-msg-bg', randomColor);
    
    // Also update the bot-avatar background color
    const botAvatars = document.querySelectorAll('.bot-avatar');
    botAvatars.forEach(avatar => {
        avatar.style.backgroundColor = randomColor;
    });
    
    // Update logo background color
    document.getElementById('bot-logo').style.backgroundColor = randomColor;
});

// Logo upload functionality
const logoUploadInput = document.getElementById('logo-upload');
const botLogo = document.getElementById('bot-logo');
const changeLogoBtn = document.getElementById('change-logo-btn');

// Trigger file input when camera button is clicked
changeLogoBtn.addEventListener('click', function() {
    logoUploadInput.click();
});

// Handle file selection
logoUploadInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file is an image
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file');
            return;
        }
        
        // Read and display the selected image
        const reader = new FileReader();
        reader.onload = function(e) {
            botLogo.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}); 