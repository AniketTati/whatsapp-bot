const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Load user settings from JSON
const CONFIG_PATH = "user_config.json";
function loadUserSettings() {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, "utf8")).users;
}

// Function to call Python script
async function callPythonBot(phoneNumber, message) {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(__dirname, 'llm_bot.py');
        // Simplified command without virtual environment activation
        const command = `python3 "${pythonScript}" "${phoneNumber}" "${message.replace(/"/g, '\\"')}"`;
        
        console.log('Executing command:', command);
        
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error('Python execution error:', error);
                reject(error);
                return;
            }
            if (stderr) {
                console.error('Python stderr:', stderr);
            }
            
            const response = stdout.trim();
            console.log('Python response:', response);
            
            if (!response) {
                reject(new Error('Empty response from Python bot'));
                return;
            }
            
            resolve(response);
        });
    });
}

// Initialize WhatsApp Client with robust configuration
const client = new Client({
    authStrategy: new LocalAuth({ clientId: "whatsapp-bot" }),
    puppeteer: {
        headless: true,
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--disable-extensions',
            '--disable-gpu',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding'
        ],
        defaultViewport: null,
        ignoreHTTPSErrors: true,
        timeout: 60000
    },
    restartOnAuthFail: true,
    qrMaxRetries: 5,
    takeoverOnConflict: true,
    takeoverTimeoutMs: 30000
});

// Handle connection events
client.on('disconnected', async (reason) => {
    console.log('WhatsApp disconnected:', reason);
    try {
        console.log('Attempting to reconnect...');
        await client.initialize();
    } catch (error) {
        console.error('Failed to reconnect:', error);
        process.exit(1); // Let nodemon restart the process
    }
});

client.on('auth_failure', (error) => {
    console.error('Authentication failed:', error);
    process.exit(1);
});

// Generate QR Code for authentication
client.on('qr', qr => {
    console.log("Scan this QR code to log in:");
    qrcode.generate(qr, { small: true });
});

// Confirm successful login
client.on('ready', () => {
    console.log("WhatsApp bot is ready!");
    startPeriodicMessages();
});

// Handle incoming messages with error handling
client.on('message', async msg => {
    try {
        if (msg.from.includes('@c.us')) {
            const chat = await msg.getChat();
            console.log('----------------------------------------');
            console.log('From:', chat.name);
            console.log('Number:', chat.id.user);
            console.log('Message:', msg.body);
            console.log('----------------------------------------');

            const phoneNumber = chat.id.user;
            const userSettings = loadUserSettings().find(user => user.phone === phoneNumber);

            if (!userSettings) return;
            console.log('User:', userSettings);

            try {
                const response = await callPythonBot(phoneNumber, msg.body);
                if (response) {
                    await client.sendMessage(msg.from, response);
                } else {
                    throw new Error('Empty response from Python bot');
                }
            } catch (error) {
                console.error('Error with Python bot:', error);
                await client.sendMessage(msg.from, "Sorry, I'm having trouble generating a response right now.");
            }
        }
    } catch (error) {
        console.error('Error handling message:', error);
    }
});

// Periodic Messages with error handling
async function startPeriodicMessages() {
    setInterval(async () => {
        try {
            const users = loadUserSettings();
            for (const user of users) {
                try {
                    const chatId = `${user.phone}@c.us`;
                    await client.sendMessage(chatId, "Hello! Hope you're having a great day! 😊");
                } catch (error) {
                    console.error(`Error sending periodic message to ${user.phone}:`, error);
                }
            }
        } catch (error) {
            console.error('Error in periodic messages:', error);
        }
    }, 60 * 60 * 1000);
}

// Error handling for uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (error) => {
    console.error('Unhandled Rejection:', error);
    process.exit(1);
});

// Initialize with error handling
(async () => {
    try {
        console.log('Starting WhatsApp bot...');
        await client.initialize();
    } catch (error) {
        console.error('Failed to initialize WhatsApp bot:', error);
        process.exit(1);
    }
})();
