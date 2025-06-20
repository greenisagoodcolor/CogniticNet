import { validateSession } from '@/lib/api-key-storage'
import { rateLimit } from '@/lib/rate-limit'
import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'

// Request schemas
const CreateAgentSchema = z.object({
  name: z.string().min(1).max(100),
  personality: z.object({
    openness: z.number().min(0).max(1),
    conscientiousness: z.number().min(0).max(1),
    extraversion: z.number().min(0).max(1),
    agreeableness: z.number().min(0).max(1),
    neuroticism: z.number().min(0).max(1)
  }),
  capabilities: z.array(z.enum([
    'movement', 'perception', 'communication', 'planning',
    'learning', 'memory', 'resource_management', 'social_interaction'
  ])).optional(),
  initialPosition: z.object({
    x: z.number(),
    y: z.number(),
    z: z.number().optional()
  }).optional(),
  tags: z.array(z.string()).optional(),
  metadata: z.record(z.any()).optional()
})

const GetAgentsQuerySchema = z.object({
  status: z.enum(['idle', 'moving', 'interacting', 'planning', 'executing', 'learning', 'error', 'offline']).optional(),
  capability: z.string().optional(),
  tag: z.string().optional(),
  limit: z.coerce.number().min(1).max(100).default(20),
  offset: z.coerce.number().min(0).default(0),
  sortBy: z.enum(['created_at', 'updated_at', 'name', 'status']).default('created_at'),
  sortOrder: z.enum(['asc', 'desc']).default('desc')
})

// Rate limiter
const limiter = rateLimit({
  interval: 60 * 1000, // 1 minute
  uniqueTokenPerInterval: 500,
})

// GET /api/agents - List agents with filtering and pagination
export async function GET(request: NextRequest) {
  try {
    // Check rate limit
    const identifier = request.ip ?? 'anonymous'
    const { success } = await limiter.check(identifier, 10)

    if (!success) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      )
    }

    // Validate session
    const sessionId = request.cookies.get('session')?.value
    const isValid = sessionId ? await validateSession('session', sessionId) : false

    if (!isValid) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Parse query parameters
    const searchParams = Object.fromEntries(request.nextUrl.searchParams)
    const query = GetAgentsQuerySchema.parse(searchParams)

    // TODO: In a real implementation, fetch from database
    // For now, return mock data
    const mockAgents = [
      {
        id: 'agent-1',
        name: 'Explorer Alpha',
        status: 'idle',
        personality: {
          openness: 0.8,
          conscientiousness: 0.7,
          extraversion: 0.6,
          agreeableness: 0.75,
          neuroticism: 0.3
        },
        capabilities: ['movement', 'perception', 'communication', 'planning'],
        position: { x: 10, y: 20, z: 0 },
        resources: {
          energy: 85,
          health: 100,
          memory_used: 2048,
          memory_capacity: 8192
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 'agent-2',
        name: 'Social Beta',
        status: 'interacting',
        personality: {
          openness: 0.6,
          conscientiousness: 0.8,
          extraversion: 0.9,
          agreeableness: 0.85,
          neuroticism: 0.2
        },
        capabilities: ['communication', 'social_interaction', 'memory'],
        position: { x: 25, y: 30, z: 0 },
        resources: {
          energy: 60,
          health: 95,
          memory_used: 4096,
          memory_capacity: 8192
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ]

    // Apply filters
    let filteredAgents = mockAgents

    if (query.status) {
      filteredAgents = filteredAgents.filter(agent => agent.status === query.status)
    }

    if (query.capability) {
      filteredAgents = filteredAgents.filter(agent =>
        agent.capabilities.includes(query.capability as any)
      )
    }

    // Apply pagination
    const total = filteredAgents.length
    const agents = filteredAgents.slice(
      query.offset,
      query.offset + query.limit
    )

    return NextResponse.json({
      agents,
      pagination: {
        total,
        limit: query.limit,
        offset: query.offset,
        hasMore: query.offset + query.limit < total
      }
    })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request parameters', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Failed to list agents:', error)
    return NextResponse.json(
      { error: 'Failed to list agents' },
      { status: 500 }
    )
  }
}

// POST /api/agents - Create a new agent
export async function POST(request: NextRequest) {
  try {
    // Check rate limit
    const identifier = request.ip ?? 'anonymous'
    const { success } = await limiter.check(identifier, 5)

    if (!success) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      )
    }

    // Validate session
    const sessionId = request.cookies.get('session')?.value
    const isValid = sessionId ? await validateSession('session', sessionId) : false

    if (!isValid) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // Parse and validate request body
    const body = await request.json()
    const data = CreateAgentSchema.parse(body)

    // TODO: In a real implementation:
    // 1. Create agent in database
    // 2. Initialize agent state
    // 3. Generate GNN model from personality
    // 4. Start agent lifecycle

    // For now, create mock response
    const newAgent = {
      id: `agent-${Date.now()}`,
      name: data.name,
      status: 'idle' as const,
      personality: data.personality,
      capabilities: data.capabilities || ['movement', 'perception', 'communication'],
      position: data.initialPosition || { x: 0, y: 0, z: 0 },
      resources: {
        energy: 100,
        health: 100,
        memory_used: 0,
        memory_capacity: 8192
      },
      tags: data.tags || [],
      metadata: data.metadata || {},
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    return NextResponse.json(
      { agent: newAgent },
      { status: 201 }
    )
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Invalid request body', details: error.errors },
        { status: 400 }
      )
    }

    console.error('Failed to create agent:', error)
    return NextResponse.json(
      { error: 'Failed to create agent' },
      { status: 500 }
    )
  }
}
