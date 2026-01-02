#!/usr/bin/env node

/**
 * MCP Server: Meta Ads
 *
 * Provides tools for interacting with Meta (Facebook/Instagram) Ads API
 *
 * Capabilities:
 * - Get campaigns, adsets, ads
 * - Get insights/metrics
 * - Create campaigns (with approval flow)
 * - Upload creatives
 *
 * Required ENV:
 * - META_ACCESS_TOKEN
 * - META_AD_ACCOUNT_ID
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const META_ACCESS_TOKEN = process.env.META_ACCESS_TOKEN;
const META_AD_ACCOUNT_ID = process.env.META_AD_ACCOUNT_ID;
const META_API_VERSION = 'v18.0';
const META_BASE_URL = `https://graph.facebook.com/${META_API_VERSION}`;

// Helper function for API calls
async function metaApiCall(endpoint, params = {}) {
  const url = new URL(`${META_BASE_URL}${endpoint}`);
  url.searchParams.append('access_token', META_ACCESS_TOKEN);

  for (const [key, value] of Object.entries(params)) {
    url.searchParams.append(key, value);
  }

  const response = await fetch(url.toString());

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Meta API Error: ${JSON.stringify(error)}`);
  }

  return response.json();
}

// Tool definitions
const tools = [
  {
    name: 'meta_get_campaigns',
    description: 'Get all campaigns from the ad account with their status and basic metrics',
    inputSchema: {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          description: 'Filter by status: ACTIVE, PAUSED, or ALL',
          enum: ['ACTIVE', 'PAUSED', 'ALL'],
          default: 'ALL'
        },
        limit: {
          type: 'number',
          description: 'Number of campaigns to return',
          default: 50
        }
      }
    }
  },
  {
    name: 'meta_get_insights',
    description: 'Get performance metrics for campaigns, adsets, or ads',
    inputSchema: {
      type: 'object',
      properties: {
        level: {
          type: 'string',
          description: 'Level of aggregation',
          enum: ['account', 'campaign', 'adset', 'ad'],
          default: 'campaign'
        },
        date_preset: {
          type: 'string',
          description: 'Date range preset',
          enum: ['today', 'yesterday', 'last_7d', 'last_14d', 'last_30d', 'this_month', 'last_month'],
          default: 'last_7d'
        },
        campaign_id: {
          type: 'string',
          description: 'Optional: specific campaign ID to get insights for'
        }
      },
      required: ['level', 'date_preset']
    }
  },
  {
    name: 'meta_get_adsets',
    description: 'Get all adsets for a specific campaign',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: {
          type: 'string',
          description: 'The campaign ID to get adsets for'
        }
      },
      required: ['campaign_id']
    }
  },
  {
    name: 'meta_get_ads',
    description: 'Get all ads for a specific adset',
    inputSchema: {
      type: 'object',
      properties: {
        adset_id: {
          type: 'string',
          description: 'The adset ID to get ads for'
        }
      },
      required: ['adset_id']
    }
  },
  {
    name: 'meta_get_ad_creatives',
    description: 'Get creative details for an ad including image/video URLs and copy',
    inputSchema: {
      type: 'object',
      properties: {
        ad_id: {
          type: 'string',
          description: 'The ad ID to get creatives for'
        }
      },
      required: ['ad_id']
    }
  },
  {
    name: 'meta_create_campaign',
    description: 'Create a new campaign (will be created in PAUSED status for approval)',
    inputSchema: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Campaign name'
        },
        objective: {
          type: 'string',
          description: 'Campaign objective',
          enum: ['CONVERSIONS', 'LEAD_GENERATION', 'TRAFFIC', 'REACH', 'VIDEO_VIEWS']
        },
        daily_budget: {
          type: 'number',
          description: 'Daily budget in cents (e.g., 5000 = $50)'
        },
        special_ad_categories: {
          type: 'array',
          items: { type: 'string' },
          description: 'Special ad categories if applicable',
          default: []
        }
      },
      required: ['name', 'objective', 'daily_budget']
    }
  },
  {
    name: 'meta_update_campaign_status',
    description: 'Update campaign status (ACTIVE or PAUSED)',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: {
          type: 'string',
          description: 'The campaign ID to update'
        },
        status: {
          type: 'string',
          description: 'New status',
          enum: ['ACTIVE', 'PAUSED']
        }
      },
      required: ['campaign_id', 'status']
    }
  },
  {
    name: 'meta_get_account_info',
    description: 'Get basic info about the ad account',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// Tool implementations
async function handleGetCampaigns({ status = 'ALL', limit = 50 }) {
  const fields = 'id,name,status,objective,daily_budget,lifetime_budget,created_time,updated_time';

  let endpoint = `/${META_AD_ACCOUNT_ID}/campaigns`;
  const params = { fields, limit: limit.toString() };

  if (status !== 'ALL') {
    params.filtering = JSON.stringify([{
      field: 'effective_status',
      operator: 'IN',
      value: [status]
    }]);
  }

  const result = await metaApiCall(endpoint, params);

  return {
    success: true,
    count: result.data.length,
    campaigns: result.data.map(c => ({
      id: c.id,
      name: c.name,
      status: c.status,
      objective: c.objective,
      daily_budget: c.daily_budget ? `$${(parseInt(c.daily_budget) / 100).toFixed(2)}` : null,
      lifetime_budget: c.lifetime_budget ? `$${(parseInt(c.lifetime_budget) / 100).toFixed(2)}` : null,
      created: c.created_time,
      updated: c.updated_time
    }))
  };
}

async function handleGetInsights({ level, date_preset, campaign_id }) {
  const fields = [
    'campaign_name',
    'adset_name',
    'ad_name',
    'spend',
    'impressions',
    'clicks',
    'ctr',
    'cpc',
    'actions',
    'cost_per_action_type',
    'reach',
    'frequency'
  ].join(',');

  let endpoint;
  if (campaign_id) {
    endpoint = `/${campaign_id}/insights`;
  } else {
    endpoint = `/${META_AD_ACCOUNT_ID}/insights`;
  }

  const params = {
    fields,
    date_preset,
    level
  };

  const result = await metaApiCall(endpoint, params);

  // Process and format the results
  const processedData = result.data.map(row => {
    const leads = row.actions?.find(a => a.action_type === 'lead')?.value || 0;
    const purchases = row.actions?.find(a => a.action_type === 'purchase')?.value || 0;
    const costPerLead = row.cost_per_action_type?.find(a => a.action_type === 'lead')?.value || null;

    return {
      campaign: row.campaign_name,
      adset: row.adset_name,
      ad: row.ad_name,
      spend: `$${parseFloat(row.spend || 0).toFixed(2)}`,
      impressions: parseInt(row.impressions || 0),
      clicks: parseInt(row.clicks || 0),
      ctr: `${parseFloat(row.ctr || 0).toFixed(2)}%`,
      cpc: `$${parseFloat(row.cpc || 0).toFixed(2)}`,
      leads: parseInt(leads),
      cpl: costPerLead ? `$${parseFloat(costPerLead).toFixed(2)}` : 'N/A',
      purchases: parseInt(purchases),
      reach: parseInt(row.reach || 0),
      frequency: parseFloat(row.frequency || 0).toFixed(2)
    };
  });

  // Calculate totals
  const totals = {
    spend: result.data.reduce((sum, r) => sum + parseFloat(r.spend || 0), 0),
    impressions: result.data.reduce((sum, r) => sum + parseInt(r.impressions || 0), 0),
    clicks: result.data.reduce((sum, r) => sum + parseInt(r.clicks || 0), 0),
    leads: result.data.reduce((sum, r) => {
      const leads = r.actions?.find(a => a.action_type === 'lead')?.value || 0;
      return sum + parseInt(leads);
    }, 0)
  };

  totals.ctr = totals.impressions > 0 ? ((totals.clicks / totals.impressions) * 100).toFixed(2) : 0;
  totals.cpl = totals.leads > 0 ? (totals.spend / totals.leads).toFixed(2) : null;

  return {
    success: true,
    date_range: date_preset,
    level,
    summary: {
      total_spend: `$${totals.spend.toFixed(2)}`,
      total_impressions: totals.impressions,
      total_clicks: totals.clicks,
      average_ctr: `${totals.ctr}%`,
      total_leads: totals.leads,
      average_cpl: totals.cpl ? `$${totals.cpl}` : 'N/A'
    },
    breakdown: processedData
  };
}

async function handleCreateCampaign({ name, objective, daily_budget, special_ad_categories = [] }) {
  // Always create in PAUSED status for human approval
  const endpoint = `/${META_AD_ACCOUNT_ID}/campaigns`;

  const params = {
    name,
    objective,
    status: 'PAUSED', // Safety: always start paused
    daily_budget: daily_budget.toString(),
    special_ad_categories: JSON.stringify(special_ad_categories)
  };

  const result = await metaApiCall(endpoint, params);

  return {
    success: true,
    message: 'Campaign created in PAUSED status. Requires human approval to activate.',
    campaign_id: result.id,
    name,
    objective,
    daily_budget: `$${(daily_budget / 100).toFixed(2)}`,
    status: 'PAUSED',
    next_step: 'Use meta_update_campaign_status to activate after review'
  };
}

async function handleUpdateStatus({ campaign_id, status }) {
  const endpoint = `/${campaign_id}`;

  const response = await fetch(`${META_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      access_token: META_ACCESS_TOKEN,
      status
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Failed to update status: ${JSON.stringify(error)}`);
  }

  return {
    success: true,
    campaign_id,
    new_status: status,
    message: `Campaign ${status === 'ACTIVE' ? 'activated' : 'paused'} successfully`
  };
}

async function handleGetAccountInfo() {
  const fields = 'id,name,account_status,currency,timezone_name,amount_spent,balance';
  const result = await metaApiCall(`/${META_AD_ACCOUNT_ID}`, { fields });

  return {
    success: true,
    account: {
      id: result.id,
      name: result.name,
      status: result.account_status === 1 ? 'ACTIVE' : 'INACTIVE',
      currency: result.currency,
      timezone: result.timezone_name,
      total_spent: result.amount_spent ? `$${(parseInt(result.amount_spent) / 100).toFixed(2)}` : 'N/A',
      balance: result.balance ? `$${(parseInt(result.balance) / 100).toFixed(2)}` : 'N/A'
    }
  };
}

// Main server setup
const server = new Server(
  {
    name: 'meta-ads-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle list tools request
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case 'meta_get_campaigns':
        result = await handleGetCampaigns(args || {});
        break;
      case 'meta_get_insights':
        result = await handleGetInsights(args);
        break;
      case 'meta_get_adsets':
        result = await handleGetAdsets(args);
        break;
      case 'meta_get_ads':
        result = await handleGetAds(args);
        break;
      case 'meta_get_ad_creatives':
        result = await handleGetCreatives(args);
        break;
      case 'meta_create_campaign':
        result = await handleCreateCampaign(args);
        break;
      case 'meta_update_campaign_status':
        result = await handleUpdateStatus(args);
        break;
      case 'meta_get_account_info':
        result = await handleGetAccountInfo();
        break;
      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: false,
            error: error.message
          }, null, 2)
        }
      ],
      isError: true
    };
  }
});

// Placeholder implementations for additional handlers
async function handleGetAdsets({ campaign_id }) {
  const fields = 'id,name,status,daily_budget,targeting,optimization_goal';
  const result = await metaApiCall(`/${campaign_id}/adsets`, { fields });
  return { success: true, adsets: result.data };
}

async function handleGetAds({ adset_id }) {
  const fields = 'id,name,status,creative';
  const result = await metaApiCall(`/${adset_id}/ads`, { fields });
  return { success: true, ads: result.data };
}

async function handleGetCreatives({ ad_id }) {
  const fields = 'id,name,effective_object_story_id,object_story_spec,thumbnail_url';
  const result = await metaApiCall(`/${ad_id}`, { fields: `creative{${fields}}` });
  return { success: true, creative: result.creative };
}

// Start the server
async function main() {
  if (!META_ACCESS_TOKEN) {
    console.error('ERROR: META_ACCESS_TOKEN environment variable is required');
    process.exit(1);
  }

  if (!META_AD_ACCOUNT_ID) {
    console.error('ERROR: META_AD_ACCOUNT_ID environment variable is required');
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Meta Ads MCP Server running...');
}

main().catch(console.error);
