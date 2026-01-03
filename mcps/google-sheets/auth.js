/**
 * Google Sheets OAuth Authentication Helper
 * Run this first: node auth.js
 * This will open browser for Google login and save tokens
 */

import { google } from 'googleapis';
import http from 'http';
import { URL } from 'url';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, '../../credentials/google-oauth.json');
const TOKEN_PATH = path.join(__dirname, '../../credentials/google-token.json');

const SCOPES = [
  'https://www.googleapis.com/auth/spreadsheets',
  'https://www.googleapis.com/auth/drive.file'
];

async function authenticate() {
  console.log('🔐 Starting Google OAuth Authentication...\n');

  // Load credentials
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    console.error('❌ Credentials file not found at:', CREDENTIALS_PATH);
    process.exit(1);
  }

  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  const { client_id, client_secret, redirect_uris } = credentials.installed;

  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    'http://localhost:3000/oauth2callback'
  );

  // Check if we already have tokens
  if (fs.existsSync(TOKEN_PATH)) {
    console.log('✅ Token already exists at:', TOKEN_PATH);
    const tokens = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));
    oauth2Client.setCredentials(tokens);

    // Test the token
    try {
      const sheets = google.sheets({ version: 'v4', auth: oauth2Client });
      console.log('✅ Token is valid!\n');
      console.log('You can now use the Google Sheets MCP.');
      return;
    } catch (error) {
      console.log('⚠️ Token expired, refreshing...\n');
    }
  }

  // Generate auth URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    prompt: 'consent'
  });

  console.log('📋 Please visit this URL to authorize the application:\n');
  console.log(authUrl);
  console.log('\n⏳ Waiting for authorization...\n');

  // Start local server to receive callback
  const code = await new Promise((resolve, reject) => {
    const server = http.createServer(async (req, res) => {
      try {
        const url = new URL(req.url, 'http://localhost:3000');
        if (url.pathname === '/oauth2callback') {
          const code = url.searchParams.get('code');

          res.writeHead(200, { 'Content-Type': 'text/html' });
          res.end(`
            <html>
              <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #34a853;">✅ Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
              </body>
            </html>
          `);

          server.close();
          resolve(code);
        }
      } catch (error) {
        reject(error);
      }
    });

    server.listen(3000, () => {
      console.log('🌐 Local server listening on http://localhost:3000');

      // Try to open browser automatically
      const openCommand = process.platform === 'darwin' ? 'open' :
                          process.platform === 'win32' ? 'start' : 'xdg-open';
      import('child_process').then(({ exec }) => {
        exec(`${openCommand} "${authUrl}"`);
      });
    });
  });

  // Exchange code for tokens
  console.log('\n🔄 Exchanging code for tokens...');
  const { tokens } = await oauth2Client.getToken(code);
  oauth2Client.setCredentials(tokens);

  // Save tokens
  fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2));
  console.log('✅ Tokens saved to:', TOKEN_PATH);

  console.log('\n🎉 Authentication complete!');
  console.log('You can now use the Google Sheets MCP.');
}

authenticate().catch(console.error);
