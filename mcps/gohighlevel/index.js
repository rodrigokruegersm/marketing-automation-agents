#!/usr/bin/env node

/**
 * MCP Server: GoHighLevel
 *
 * Provides tools for interacting with GoHighLevel CRM API
 *
 * Capabilities:
 * - Get contacts, opportunities, pipelines
 * - Get calendar appointments
 * - Get conversations
 * - Read analytics
 *
 * Required ENV:
 * - GHL_API_KEY (Location/Sub-account API Key)
 * - GHL_LOCATION_ID
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const GHL_API_KEY = process.env.GHL_API_KEY;
const GHL_LOCATION_ID = process.env.GHL_LOCATION_ID;
const GHL_BASE_URL = 'https://services.leadconnectorhq.com';

// Helper function for API calls
async function ghlApiCall(endpoint, method = 'GET', body = null) {
  const url = `${GHL_BASE_URL}${endpoint}`;

  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${GHL_API_KEY}`,
      'Content-Type': 'application/json',
      'Version': '2021-07-28'
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(url, options);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`GHL API Error: ${response.status} - ${error}`);
  }

  return response.json();
}

// Tool definitions
const tools = [
  {
    name: 'ghl_get_contacts',
    description: 'Get contacts from GoHighLevel with optional filters',
    inputSchema: {
      type: 'object',
      properties: {
        limit: {
          type: 'number',
          description: 'Number of contacts to return',
          default: 20
        },
        query: {
          type: 'string',
          description: 'Search query (name, email, phone)'
        }
      }
    }
  },
  {
    name: 'ghl_get_contact',
    description: 'Get a specific contact by ID',
    inputSchema: {
      type: 'object',
      properties: {
        contact_id: {
          type: 'string',
          description: 'The contact ID'
        }
      },
      required: ['contact_id']
    }
  },
  {
    name: 'ghl_get_opportunities',
    description: 'Get opportunities/deals from a pipeline',
    inputSchema: {
      type: 'object',
      properties: {
        pipeline_id: {
          type: 'string',
          description: 'Pipeline ID to filter by'
        },
        status: {
          type: 'string',
          description: 'Filter by status',
          enum: ['open', 'won', 'lost', 'all'],
          default: 'all'
        },
        limit: {
          type: 'number',
          default: 20
        }
      }
    }
  },
  {
    name: 'ghl_get_pipelines',
    description: 'Get all pipelines in the location',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'ghl_get_appointments',
    description: 'Get calendar appointments',
    inputSchema: {
      type: 'object',
      properties: {
        calendar_id: {
          type: 'string',
          description: 'Calendar ID to filter by'
        },
        start_date: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)'
        },
        end_date: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)'
        }
      },
      required: ['start_date', 'end_date']
    }
  },
  {
    name: 'ghl_get_calendars',
    description: 'Get all calendars in the location',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'ghl_get_conversations',
    description: 'Get recent conversations/messages',
    inputSchema: {
      type: 'object',
      properties: {
        contact_id: {
          type: 'string',
          description: 'Filter by contact ID'
        },
        limit: {
          type: 'number',
          default: 20
        }
      }
    }
  },
  {
    name: 'ghl_get_location_stats',
    description: 'Get location statistics and metrics',
    inputSchema: {
      type: 'object',
      properties: {
        start_date: {
          type: 'string',
          description: 'Start date (YYYY-MM-DD)'
        },
        end_date: {
          type: 'string',
          description: 'End date (YYYY-MM-DD)'
        }
      }
    }
  }
];

// Tool implementations
async function handleGetContacts({ limit = 20, query }) {
  let endpoint = `/contacts/?locationId=${GHL_LOCATION_ID}&limit=${limit}`;
  if (query) {
    endpoint += `&query=${encodeURIComponent(query)}`;
  }

  const result = await ghlApiCall(endpoint);

  return {
    success: true,
    count: result.contacts?.length || 0,
    contacts: result.contacts?.map(c => ({
      id: c.id,
      name: `${c.firstName || ''} ${c.lastName || ''}`.trim(),
      email: c.email,
      phone: c.phone,
      tags: c.tags,
      source: c.source,
      created: c.dateAdded
    })) || []
  };
}

async function handleGetContact({ contact_id }) {
  const result = await ghlApiCall(`/contacts/${contact_id}`);

  return {
    success: true,
    contact: {
      id: result.contact.id,
      name: `${result.contact.firstName || ''} ${result.contact.lastName || ''}`.trim(),
      email: result.contact.email,
      phone: result.contact.phone,
      tags: result.contact.tags,
      source: result.contact.source,
      customFields: result.contact.customField,
      created: result.contact.dateAdded
    }
  };
}

async function handleGetOpportunities({ pipeline_id, status = 'all', limit = 20 }) {
  let endpoint = `/opportunities/search?locationId=${GHL_LOCATION_ID}&limit=${limit}`;

  if (pipeline_id) {
    endpoint += `&pipelineId=${pipeline_id}`;
  }

  if (status !== 'all') {
    endpoint += `&status=${status}`;
  }

  const result = await ghlApiCall(endpoint);

  return {
    success: true,
    count: result.opportunities?.length || 0,
    opportunities: result.opportunities?.map(o => ({
      id: o.id,
      name: o.name,
      value: o.monetaryValue ? `$${o.monetaryValue}` : 'N/A',
      status: o.status,
      stage: o.pipelineStageId,
      contact: o.contactId,
      created: o.createdAt
    })) || []
  };
}

async function handleGetPipelines() {
  const result = await ghlApiCall(`/opportunities/pipelines?locationId=${GHL_LOCATION_ID}`);

  return {
    success: true,
    pipelines: result.pipelines?.map(p => ({
      id: p.id,
      name: p.name,
      stages: p.stages?.map(s => ({
        id: s.id,
        name: s.name,
        position: s.position
      }))
    })) || []
  };
}

async function handleGetAppointments({ calendar_id, start_date, end_date }) {
  let endpoint = `/calendars/events?locationId=${GHL_LOCATION_ID}&startTime=${start_date}&endTime=${end_date}`;

  if (calendar_id) {
    endpoint += `&calendarId=${calendar_id}`;
  }

  const result = await ghlApiCall(endpoint);

  return {
    success: true,
    count: result.events?.length || 0,
    appointments: result.events?.map(e => ({
      id: e.id,
      title: e.title,
      status: e.appointmentStatus,
      start: e.startTime,
      end: e.endTime,
      contact: e.contactId,
      calendar: e.calendarId
    })) || []
  };
}

async function handleGetCalendars() {
  const result = await ghlApiCall(`/calendars/?locationId=${GHL_LOCATION_ID}`);

  return {
    success: true,
    calendars: result.calendars?.map(c => ({
      id: c.id,
      name: c.name,
      description: c.description,
      isActive: c.isActive
    })) || []
  };
}

async function handleGetConversations({ contact_id, limit = 20 }) {
  let endpoint = `/conversations/search?locationId=${GHL_LOCATION_ID}&limit=${limit}`;

  if (contact_id) {
    endpoint += `&contactId=${contact_id}`;
  }

  const result = await ghlApiCall(endpoint);

  return {
    success: true,
    count: result.conversations?.length || 0,
    conversations: result.conversations?.map(c => ({
      id: c.id,
      contactId: c.contactId,
      type: c.type,
      lastMessage: c.lastMessageBody,
      lastMessageDate: c.lastMessageDate,
      unread: c.unreadCount
    })) || []
  };
}

async function handleGetLocationStats({ start_date, end_date }) {
  // GHL doesn't have a direct stats endpoint, so we aggregate from other sources
  const [contacts, opportunities, appointments] = await Promise.all([
    ghlApiCall(`/contacts/?locationId=${GHL_LOCATION_ID}&limit=1`).catch(() => ({ meta: { total: 0 } })),
    ghlApiCall(`/opportunities/search?locationId=${GHL_LOCATION_ID}&limit=100`).catch(() => ({ opportunities: [] })),
    start_date && end_date ? ghlApiCall(`/calendars/events?locationId=${GHL_LOCATION_ID}&startTime=${start_date}&endTime=${end_date}`).catch(() => ({ events: [] })) : { events: [] }
  ]);

  const opps = opportunities.opportunities || [];
  const wonOpps = opps.filter(o => o.status === 'won');
  const totalValue = wonOpps.reduce((sum, o) => sum + (o.monetaryValue || 0), 0);

  return {
    success: true,
    stats: {
      total_contacts: contacts.meta?.total || 0,
      total_opportunities: opps.length,
      won_opportunities: wonOpps.length,
      total_revenue: `$${totalValue.toFixed(2)}`,
      appointments_in_period: appointments.events?.length || 0,
      conversion_rate: opps.length > 0 ? `${((wonOpps.length / opps.length) * 100).toFixed(1)}%` : 'N/A'
    }
  };
}

// Main server setup
const server = new Server(
  {
    name: 'gohighlevel-mcp',
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
      case 'ghl_get_contacts':
        result = await handleGetContacts(args || {});
        break;
      case 'ghl_get_contact':
        result = await handleGetContact(args);
        break;
      case 'ghl_get_opportunities':
        result = await handleGetOpportunities(args || {});
        break;
      case 'ghl_get_pipelines':
        result = await handleGetPipelines();
        break;
      case 'ghl_get_appointments':
        result = await handleGetAppointments(args);
        break;
      case 'ghl_get_calendars':
        result = await handleGetCalendars();
        break;
      case 'ghl_get_conversations':
        result = await handleGetConversations(args || {});
        break;
      case 'ghl_get_location_stats':
        result = await handleGetLocationStats(args || {});
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
  if (!GHL_API_KEY) {
    console.error('ERROR: GHL_API_KEY environment variable is required');
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('GoHighLevel MCP Server running...');
}

main().catch(console.error);
