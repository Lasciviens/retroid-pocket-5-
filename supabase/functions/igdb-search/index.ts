import { corsHeaders } from 'npm:@supabase/supabase-js/cors'

type IgdbTokenResponse = {
  access_token: string
  expires_in: number
  token_type: string
}

const TWITCH_CLIENT_ID =
  Deno.env.get('TWITCH_CLIENT_ID') ||
  Deno.env.get('IGDB_CLIENT_ID') ||
  ''

const TWITCH_CLIENT_SECRET =
  Deno.env.get('TWITCH_CLIENT_SECRET') ||
  Deno.env.get('IGDB_CLIENT_SECRET') ||
  ''

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      ...corsHeaders,
      'Content-Type': 'application/json; charset=utf-8',
    },
  })
}

async function getAccessToken() {
  const url = new URL('https://id.twitch.tv/oauth2/token')
  url.searchParams.set('client_id', TWITCH_CLIENT_ID)
  url.searchParams.set('client_secret', TWITCH_CLIENT_SECRET)
  url.searchParams.set('grant_type', 'client_credentials')

  const response = await fetch(url, { method: 'POST' })
  if (!response.ok) {
    throw new Error(`Token request failed: ${response.status}`)
  }

  return (await response.json()) as IgdbTokenResponse
}

function buildApicalypseQuery(title: string) {
  const escaped = title.replace(/"/g, '\\"')
  return [
    'fields name,slug,summary,total_rating,first_release_date,cover.url,genres.name,platforms.abbreviation,involved_companies.company.name;',
    `search "${escaped}";`,
    'where version_parent = null;',
    'limit 8;',
  ].join(' ')
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (!TWITCH_CLIENT_ID || !TWITCH_CLIENT_SECRET) {
    return json(
      {
        error: 'Missing secrets',
        required: ['TWITCH_CLIENT_ID', 'TWITCH_CLIENT_SECRET'],
      },
      500,
    )
  }

  const { searchParams } = new URL(req.url)
  const title = (searchParams.get('title') || '').trim()
  if (!title) {
    return json({ error: 'Missing title query parameter' }, 400)
  }

  try {
    const token = await getAccessToken()
    const igdbResponse = await fetch('https://api.igdb.com/v4/games', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': `Bearer ${token.access_token}`,
      },
      body: buildApicalypseQuery(title),
    })

    if (!igdbResponse.ok) {
      const details = await igdbResponse.text()
      return json(
        {
          error: 'IGDB request failed',
          status: igdbResponse.status,
          details,
        },
        502,
      )
    }

    const results = await igdbResponse.json()
    return json({ query: title, results })
  } catch (error) {
    return json(
      {
        error: 'Unexpected proxy failure',
        details: error instanceof Error ? error.message : String(error),
      },
      500,
    )
  }
})
