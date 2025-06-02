
import { type NextRequest, NextResponse } from "next/server"
import { retrieveApiKey } from "@/lib/api-key-service-server"  // ← Change this import

export async function POST(request: NextRequest) {  // ← Change GET to POST
  try {
    const { provider, sessionId } = await request.json()  // ← Get from body, not query params
    
    // Validate input
    if (!provider || !sessionId) {
      return NextResponse.json(
        { error: "Provider and sessionId are required" },
        { status: 400 }
      )
    }
    
    // Retrieve the API key
    const apiKey = await retrieveApiKey(provider, sessionId)  // ← Function name change
    
    if (!apiKey) {
      return NextResponse.json(
        { error: "API key not found" },
        { status: 404 }
      )
    }
    
    return NextResponse.json({ apiKey })
  } catch (error) {
    console.error("[API] Error retrieving API key:", error)
    return NextResponse.json(
      { error: "Failed to retrieve API key" },
      { status: 500 }
    )
  }
}