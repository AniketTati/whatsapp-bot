const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' // Correct path for Mac
    }
});

// Generate QR Code for authentication
client.on('qr', qr => {
    console.log('Scan this QR code with your phone:');
    qrcode.generate(qr, { small: true });
});

// When logged in
client.on('ready', () => {
    console.log('Bot is ready!');
});

// Auto-reply when a specific friend messages you
const friendName = 'Aniket T'; // Change this to your friend's name
const friendNumber = '919969982534'; // Change this to your friend's number

client.on('message', async msg => {
    if (msg.from.includes('@c.us')) { // Only respond to individual messages
        const chat = await msg.getChat();
        const senderName = chat.name;
        const senderNumber = chat.id.user;
        const messageText = msg.body;
        
        console.log('----------------------------------------');
        console.log('From:', senderName);
        console.log('Number:', senderNumber);
        console.log('Message:', messageText);
        console.log('----------------------------------------');

        if (chat.name === friendName || chat.id.user === friendNumber) {
            console.log(`Message from ${friendName}: ${msg.body}`);

            // Reply with an LLM response
            const response = await getLLMResponse(msg.body);
            client.sendMessage(msg.from, response);
        }
    }
});

// Function to get LLM response (Replace with your actual LLM call)
async function getLLMResponse(message) {
    return `AI Reply: You said "${message}"`; // Replace with LLM API call
}

// Send a hello message every hour
setInterval(() => {
    sendPeriodicMessage();
}, 60 * 60 * 1000); // Every 1 hour

async function sendPeriodicMessage() {
    const chats = await client.getChats();
    const friendChat = chats.find(chat => chat.name === friendName);

    if (friendChat) {
        client.sendMessage(friendChat.id._serialized, 'Hello! How are you?');
        console.log('Sent periodic hello message.');
    }
}

// Start the bot
client.initialize();
