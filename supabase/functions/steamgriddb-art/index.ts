import { corsHeaders } from 'npm:@supabase/supabase-js/cors'

const SGDB_API_KEY = Deno.env.get('STEAMGRIDDB_API_KEY') || ''
const SGDB_BASE = 'https://www.steamgriddb.com/api/v2'

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
}

async function sgdb(path: string) {
  const response = await fetch(`${SGDB_BASE}${path}`, {
    headers: {
      Authorization: `Bearer ${SGDB_API_KEY}`,
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    const details = await response.text()
    throw new Error(`SteamGridDB request failed: ${response.status} ${details}`)
  }

  return await response.json()
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (!SGDB_API_KEY) {
    return json({ error: 'Missing secrets', required: ['STEAMGRIDDB_API_KEY'] }, 500)
  }

  const { searchParams } = new URL(req.url)
  const title = (searchParams.get('title') || '').trim()
  const gameId = (searchParams.get('gameId') || '').trim()
  const asset = (searchParams.get('asset') || 'grids').trim()

  try {
    if (title) {
      const search = await sgdb(`/search/autocomplete/${encodeURIComponent(title)}`)
      return json({ mode: 'search', title, asset, data: search })
    }

    if (gameId) {
      const normalizedAsset = ['grids', 'heroes', 'logos', 'icons'].includes(asset) ? asset : 'grids'
      const data = await sgdb(`/${normalizedAsset}/game/${encodeURIComponent(gameId)}`)
      return json({ mode: 'asset', gameId, asset: normalizedAsset, data })
    }

    return json(
      {
        error: 'Missing title or gameId query parameter',
        examples: ['?title=Chrono%20Trigger', '?gameId=12345&asset=heroes'],
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
