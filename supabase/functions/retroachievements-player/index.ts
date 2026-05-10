import { corsHeaders } from 'npm:@supabase/supabase-js/cors'

const RA_USERNAME = Deno.env.get('RETROACHIEVEMENTS_USERNAME') || ''
const RA_WEB_API_KEY = Deno.env.get('RETROACHIEVEMENTS_WEB_API_KEY') || ''

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
}

async function callRa(path: string, params: Record<string, string>) {
  const url = new URL(`https://retroachievements.org${path}`)
  url.searchParams.set('z', RA_USERNAME)
  url.searchParams.set('y', RA_WEB_API_KEY)
  Object.entries(params).forEach(([key, value]) => url.searchParams.set(key, value))

  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`RetroAchievements request failed: ${response.status}`)
  }
  return await response.json()
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (!RA_USERNAME || !RA_WEB_API_KEY) {
    return json(
      {
        error: 'Missing secrets',
        required: ['RETROACHIEVEMENTS_USERNAME', 'RETROACHIEVEMENTS_WEB_API_KEY'],
      },
      500,
    )
  }

  const { searchParams } = new URL(req.url)
  const mode = (searchParams.get('mode') || 'summary').trim()
  const username = (searchParams.get('username') || '').trim()
  const gameId = (searchParams.get('gameId') || '').trim()

  try {
    if (mode === 'summary' && username) {
      const data = await callRa('/API/API_GetUserSummary.php', { u: username })
      return json({ mode, username, data })
    }

    if (mode === 'game-progress' && username && gameId) {
      const data = await callRa('/API/API_GetGameInfoAndUserProgress.php', {
        u: username,
        g: gameId,
      })
      return json({ mode, username, gameId, data })
    }

    if (mode === 'completion' && username) {
      const data = await callRa('/API/API_GetUserCompletionProgress.php', { u: username })
      return json({ mode, username, data })
    }

    return json(
      {
        error: 'Missing or invalid query parameters',
        examples: [
          '?mode=summary&username=YourName',
          '?mode=completion&username=YourName',
          '?mode=game-progress&username=YourName&gameId=14402',
        ],
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
