import { corsHeaders } from 'npm:@supabase/supabase-js/cors'

const RAWG_API_KEY = Deno.env.get('RAWG_API_KEY') || ''
const RAWG_BASE = 'https://api.rawg.io/api'

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
}

async function rawg(path: string, params: Record<string, string>) {
  const url = new URL(`${RAWG_BASE}${path}`)
  url.searchParams.set('key', RAWG_API_KEY)
  Object.entries(params).forEach(([key, value]) => {
    if (value) url.searchParams.set(key, value)
  })

  const response = await fetch(url)
  if (!response.ok) {
    const details = await response.text()
    throw new Error(`RAWG request failed: ${response.status} ${details}`)
  }
  return await response.json()
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (!RAWG_API_KEY) {
    return json({ error: 'Missing secrets', required: ['RAWG_API_KEY'] }, 500)
  }

  const { searchParams } = new URL(req.url)
  const mode = (searchParams.get('mode') || 'search').trim()
  const title = (searchParams.get('title') || '').trim()
  const gameId = (searchParams.get('gameId') || '').trim()

  try {
    if (mode === 'search' && title) {
      const data = await rawg('/games', { search: title, page_size: '10' })
      return json({ mode, title, data })
    }

    if (mode === 'details' && gameId) {
      const data = await rawg(`/games/${encodeURIComponent(gameId)}`, {})
      return json({ mode, gameId, data })
    }

    if (mode === 'suggested' && gameId) {
      const data = await rawg(`/games/${encodeURIComponent(gameId)}/suggested`, { page_size: '12' })
      return json({ mode, gameId, data })
    }

    return json(
      {
        error: 'Missing or invalid query parameters',
        examples: ['?mode=search&title=Metroid', '?mode=details&gameId=3498', '?mode=suggested&gameId=3498'],
      },
      400,
    )
  } catch (error) {
    return json(
      { error: 'Unexpected proxy failure', details: error instanceof Error ? error.message : String(error) },
      500,
    )
  }
})
