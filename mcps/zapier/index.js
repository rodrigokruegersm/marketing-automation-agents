#!/usr/bin/env node

/**
 * MCP Server: Zapier
 *
 * Provides tools for interacting with Zapier API
 *
 * Capabilities:
 * - List Zaps and their status
 * - Enable/disable Zaps
 * - View Zap run history
 * - Trigger webhooks
 *
 * Required ENV:
 * - ZAPIER_API_KEY (from Zapier Developer Platform)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const ZAPIER_API_KEY = process.env.ZAPIER_API_KEY;
const ZAPIER_BASE_URL = 'https://api.zapier.com/v1';

// Helper function for API calls
async function zapierApiCall(endpoint, method = 'GET', body = null) {
  const url = `${ZAPIER_BASE_URL}${endpoint}`;

  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${ZAPIER_API_KEY}`,
      'Content-Type': 'application/json'
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Zapier API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

// Tool definitions
const tools = [
  {
    name: 'zapier_list_zaps',
    description: 'List all Zaps in the account with their status',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          description: 'Filter by status',
          enum: ['on', 'off', 'all'],
          default: 'all'
        }
      }
    }
  },
  {
    name: 'zapier_get_zap',
    description: 'Get details of a specific Zap',
    inputSchema: {
      type: 'object',
      properties: {
        zap_id: {
          type: 'string',
          description: 'The Zap ID'
        }
      },
      required: ['zap_id']
    }
  },
  {
    name: 'zapier_enable_zap',
    description: 'Turn on a Zap',
    inputSchema: {
      type: 'object',
      properties: {
        zap_id: {
          type: 'string',
          description: 'The Zap ID to enable'
        }
      },
      required: ['zap_id']
    }
  },
  {
    name: 'zapier_disable_zap',
    description: 'Turn off a Zap',
    inputSchema: {
      type: 'object',
      properties: {
        zap_id: {
          type: 'string',
          description: 'The Zap ID to disable'
        }
      },
      required: ['zap_id']
    }
  },
  {
    name: 'zapier_get_zap_runs',
    description: 'Get run history for a specific Zap',
    inputSchema: {
      type: 'object',
      properties: {
        zap_id: {
          type: 'string',
          description: 'The Zap ID'
        },
        status: {
          type: 'string',
          description: 'Filter by run status',
          enum: ['success', 'error', 'all'],
          default: 'all'
        },
        limit: {
          type: 'number',
          default: 10
        }
      },
      required: ['zap_id']
    }
  },
  {
    name: 'zapier_trigger_webhook',
    description: 'Trigger a Zapier webhook URL with custom data',
    inputSchema: {
      type: 'object',
      properties: {
        webhook_url: {
          type: 'string',
          description: 'The Zapier webhook URL'
        },
        data: {
          type: 'object',
          description: 'Data to send to the webhook'
        }
      },
      required: ['webhook_url', 'data']
    }
  },
  {
    name: 'zapier_get_account_status',
    description: 'Get account status including task usage',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// Tool implementations
async function handleListZaps({ status = 'all' }) {
  const result = await zapierApiCall('/zaps');

  let zaps = result.data || [];

  if (status !== 'all') {
    const isOn = status === 'on';
    zaps = zaps.filter(z => z.is_enabled === isOn);
  }

  return {
    success: true,
    count: zaps.length,
    zaps: zaps.map(z => ({
      id: z.id,
      title: z.title,
      status: z.is_enabled ? 'ON' : 'OFF',
      trigger_app: z.steps?.[0]?.app?.name || 'Unknown',
      action_apps: z.steps?.slice(1).map(s => s.app?.name).filter(Boolean) || [],
      last_run: z.last_run_at,
      created: z.created_at
    }))
  };
}

async function handleGetZap({ zap_id }) {
  const result = await zapierApiCall(`/zaps/${zap_id}`);

  return {
    success: true,
    zap: {
      id: result.id,
      title: result.title,
      status: result.is_enabled ? 'ON' : 'OFF',
      steps: result.steps?.map(s => ({
        position: s.position,
        app: s.app?.name,
        action: s.action?.name
      })),
      last_run: result.last_run_at,
      created: result.created_at,
      modified: result.modified_at
    }
  };
}

async function handleEnableZap({ zap_id }) {
  // Note: Zapier API v1 may have limitations on enabling/disabling
  // This is a placeholder - actual implementation depends on API version
  try {
    await zapierApiCall(`/zaps/${zap_id}`, 'PATCH', { is_enabled: true });
    return {
      success: true,
      message: `Zap ${zap_id} has been enabled`,
      zap_id,
      new_status: 'ON'
    };
  } catch (error) {
    return {
      success: false,
      message: 'Unable to enable Zap via API. Please enable manually in Zapier dashboard.',
      zap_id,
      error: error.message
    };
  }
}

async function handleDisableZap({ zap_id }) {
  try {
    await zapierApiCall(`/zaps/${zap_id}`, 'PATCH', { is_enabled: false });
    return {
      success: true,
      message: `Zap ${zap_id} has been disabled`,
      zap_id,
      new_status: 'OFF'
    };
  } catch (error) {
    return {
      success: false,
      message: 'Unable to disable Zap via API. Please disable manually in Zapier dashboard.',
      zap_id,
      error: error.message
    };
  }
}

async function handleGetZapRuns({ zap_id, status = 'all', limit = 10 }) {
  let endpoint = `/zaps/${zap_id}/runs?limit=${limit}`;

  const result = await zapierApiCall(endpoint);

  let runs = result.data || [];

  if (status !== 'all') {
    runs = runs.filter(r => r.status === status);
  }

  return {
    success: true,
    count: runs.length,
    runs: runs.map(r => ({
      id: r.id,
      status: r.status,
      started: r.started_at,
      finished: r.finished_at,
      duration_ms: r.duration,
      steps_run: r.steps_count,
      error: r.status === 'error' ? r.error_message : null
    }))
  };
}

async function handleTriggerWebhook({ webhook_url, data }) {
  const response = await fetch(webhook_url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });

  const responseText = await response.text();

  return {
    success: response.ok,
    status_code: response.status,
    response: responseText,
    message: response.ok ? 'Webhook triggered successfully' : 'Webhook trigger failed'
  };
}

async function handleGetAccountStatus() {
  try {
    const result = await zapierApiCall('/profile');

    return {
      success: true,
      account: {
        email: result.email,
        plan: result.plan_name,
        tasks_used: result.tasks_used,
        tasks_limit: result.tasks_limit,
        tasks_remaining: result.tasks_limit - result.tasks_used,
        zaps_count: result.zaps_count
      }
    };
  } catch (error) {
    return {
      success: false,
      error: 'Unable to fetch account status',
      message: error.message
    };
  }
}

// Main server setup
const server = new Server(
  {
    name: 'zapier-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case 'zapier_list_zaps':
        result = await handleListZaps(args || {});
        break;
      case 'zapier_get_zap':
        result = await handleGetZap(args);
        break;
      case 'zapier_enable_zap':
        result = await handleEnableZap(args);
        break;
      case 'zapier_disable_zap':
        result = await handleDisableZap(args);
        break;
      case 'zapier_get_zap_runs':
        result = await handleGetZapRuns(args);
        break;
      case 'zapier_trigger_webhook':
        result = await handleTriggerWebhook(args);
        break;
      case 'zapier_get_account_status':
        result = await handleGetAccountStatus();
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
    };
  } catch (error) {
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: false, error: error.message }, null, 2) }],
      isError: true
    };
  }
});

async function main() {
  if (!ZAPIER_API_KEY) {
    console.error('ERROR: ZAPIER_API_KEY environment variable is required');
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Zapier MCP Server running...');
}

main().catch(console.error);
