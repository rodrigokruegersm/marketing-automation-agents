#!/usr/bin/env node

/**
 * Google Sheets MCP Server
 * Provides tools to read, write, and manage Google Sheets
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const CREDENTIALS_PATH = path.join(__dirname, '../../credentials/google-oauth.json');
const TOKEN_PATH = path.join(__dirname, '../../credentials/google-token.json');

// Initialize OAuth client
function getAuthClient() {
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    throw new Error('Credentials file not found. Run: node auth.js first');
  }

  if (!fs.existsSync(TOKEN_PATH)) {
    throw new Error('Token file not found. Run: node auth.js first');
  }

  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  const tokens = JSON.parse(fs.readFileSync(TOKEN_PATH, 'utf8'));

  const { client_id, client_secret } = credentials.installed;

  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    'http://localhost:3000/oauth2callback'
  );

  oauth2Client.setCredentials(tokens);
  return oauth2Client;
}

// Create server
const server = new Server(
  {
    name: 'google-sheets-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'sheets_create',
        description: 'Create a new Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            title: {
              type: 'string',
              description: 'Title of the spreadsheet'
            },
            sheets: {
              type: 'array',
              items: { type: 'string' },
              description: 'Names of sheets to create'
            }
          },
          required: ['title']
        }
      },
      {
        name: 'sheets_read',
        description: 'Read data from a Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            },
            range: {
              type: 'string',
              description: 'The A1 notation range to read (e.g., Sheet1!A1:Z100)'
            }
          },
          required: ['spreadsheetId', 'range']
        }
      },
      {
        name: 'sheets_write',
        description: 'Write data to a Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            },
            range: {
              type: 'string',
              description: 'The A1 notation range to write (e.g., Sheet1!A1)'
            },
            values: {
              type: 'array',
              items: {
                type: 'array',
                items: { type: 'string' }
              },
              description: '2D array of values to write'
            }
          },
          required: ['spreadsheetId', 'range', 'values']
        }
      },
      {
        name: 'sheets_append',
        description: 'Append data to a Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            },
            range: {
              type: 'string',
              description: 'The A1 notation range to append to (e.g., Sheet1!A:Z)'
            },
            values: {
              type: 'array',
              items: {
                type: 'array',
                items: { type: 'string' }
              },
              description: '2D array of values to append'
            }
          },
          required: ['spreadsheetId', 'range', 'values']
        }
      },
      {
        name: 'sheets_clear',
        description: 'Clear data from a range in a Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            },
            range: {
              type: 'string',
              description: 'The A1 notation range to clear'
            }
          },
          required: ['spreadsheetId', 'range']
        }
      },
      {
        name: 'sheets_get_info',
        description: 'Get information about a Google Spreadsheet',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            }
          },
          required: ['spreadsheetId']
        }
      },
      {
        name: 'sheets_push_meta_data',
        description: 'Push Meta Ads data to a Google Spreadsheet (pre-configured for Brez Scales)',
        inputSchema: {
          type: 'object',
          properties: {
            spreadsheetId: {
              type: 'string',
              description: 'The ID of the spreadsheet'
            },
            data: {
              type: 'object',
              description: 'Meta Ads data object with metrics',
              properties: {
                date: { type: 'string' },
                spend: { type: 'number' },
                revenue: { type: 'number' },
                impressions: { type: 'number' },
                reach: { type: 'number' },
                frequency: { type: 'number' },
                cpm: { type: 'number' },
                clicks: { type: 'number' },
                cpc: { type: 'number' },
                ctr: { type: 'number' },
                link_clicks: { type: 'number' },
                lp_views: { type: 'number' },
                init_checkout: { type: 'number' },
                add_payment: { type: 'number' },
                purchases: { type: 'number' },
                roas: { type: 'number' }
              }
            }
          },
          required: ['spreadsheetId', 'data']
        }
      }
    ]
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    const auth = getAuthClient();
    const sheets = google.sheets({ version: 'v4', auth });
    const drive = google.drive({ version: 'v3', auth });

    switch (name) {
      case 'sheets_create': {
        const { title, sheets: sheetNames = ['Sheet1'] } = args;

        const response = await sheets.spreadsheets.create({
          requestBody: {
            properties: { title },
            sheets: sheetNames.map(name => ({
              properties: { title: name }
            }))
          }
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              spreadsheetId: response.data.spreadsheetId,
              spreadsheetUrl: response.data.spreadsheetUrl,
              title: response.data.properties.title
            }, null, 2)
          }]
        };
      }

      case 'sheets_read': {
        const { spreadsheetId, range } = args;

        const response = await sheets.spreadsheets.values.get({
          spreadsheetId,
          range
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              range: response.data.range,
              values: response.data.values || []
            }, null, 2)
          }]
        };
      }

      case 'sheets_write': {
        const { spreadsheetId, range, values } = args;

        const response = await sheets.spreadsheets.values.update({
          spreadsheetId,
          range,
          valueInputOption: 'USER_ENTERED',
          requestBody: { values }
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              updatedRange: response.data.updatedRange,
              updatedRows: response.data.updatedRows,
              updatedColumns: response.data.updatedColumns,
              updatedCells: response.data.updatedCells
            }, null, 2)
          }]
        };
      }

      case 'sheets_append': {
        const { spreadsheetId, range, values } = args;

        const response = await sheets.spreadsheets.values.append({
          spreadsheetId,
          range,
          valueInputOption: 'USER_ENTERED',
          insertDataOption: 'INSERT_ROWS',
          requestBody: { values }
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              updatedRange: response.data.updates.updatedRange,
              updatedRows: response.data.updates.updatedRows
            }, null, 2)
          }]
        };
      }

      case 'sheets_clear': {
        const { spreadsheetId, range } = args;

        await sheets.spreadsheets.values.clear({
          spreadsheetId,
          range
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: `Cleared range: ${range}`
            }, null, 2)
          }]
        };
      }

      case 'sheets_get_info': {
        const { spreadsheetId } = args;

        const response = await sheets.spreadsheets.get({
          spreadsheetId
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              title: response.data.properties.title,
              locale: response.data.properties.locale,
              sheets: response.data.sheets.map(s => ({
                title: s.properties.title,
                sheetId: s.properties.sheetId,
                rowCount: s.properties.gridProperties.rowCount,
                columnCount: s.properties.gridProperties.columnCount
              })),
              spreadsheetUrl: response.data.spreadsheetUrl
            }, null, 2)
          }]
        };
      }

      case 'sheets_push_meta_data': {
        const { spreadsheetId, data } = args;

        // Calculate derived metrics
        const profit = data.revenue - data.spend;
        const margin = data.revenue > 0 ? (profit / data.revenue * 100).toFixed(2) : 0;
        const commission = profit * 0.20;
        const cplv = data.lp_views > 0 ? (data.spend / data.lp_views).toFixed(2) : 0;
        const cpic = data.init_checkout > 0 ? (data.spend / data.init_checkout).toFixed(2) : 0;
        const cpapi = data.add_payment > 0 ? (data.spend / data.add_payment).toFixed(2) : 0;
        const cpp = data.purchases > 0 ? (data.spend / data.purchases).toFixed(2) : 0;

        const row = [
          data.date,
          data.spend,
          data.revenue,
          data.impressions,
          data.reach,
          data.frequency,
          data.cpm,
          data.clicks,
          data.cpc,
          data.ctr,
          data.link_clicks,
          data.lp_views,
          cplv,
          data.init_checkout,
          cpic,
          data.add_payment,
          cpapi,
          data.purchases,
          data.revenue / data.purchases, // AOV
          cpp,
          data.roas,
          profit,
          margin,
          commission
        ];

        const response = await sheets.spreadsheets.values.append({
          spreadsheetId,
          range: 'Data!A:X',
          valueInputOption: 'USER_ENTERED',
          insertDataOption: 'INSERT_ROWS',
          requestBody: {
            values: [row]
          }
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              message: 'Meta Ads data pushed successfully',
              updatedRange: response.data.updates.updatedRange,
              metrics: {
                date: data.date,
                spend: data.spend,
                revenue: data.revenue,
                roas: data.roas,
                profit,
                commission
              }
            }, null, 2)
          }]
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          error: error.message
        }, null, 2)
      }],
      isError: true
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Google Sheets MCP Server running on stdio');
}

main().catch(console.error);
