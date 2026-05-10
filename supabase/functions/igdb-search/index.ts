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

function sharedFields() {
  return [
    'name',
    'slug',
    'summary',
    'storyline',
    'total_rating',
    'first_release_date',
    'cover.url',
    'genres.name',
    'platforms.name',
    'platforms.abbreviation',
    'involved_companies.developer',
    'involved_companies.publisher',
    'involved_companies.company.name',
    'franchises.name',
    'collections.name',
    'multiplayer_modes.offlinecoop',
    'multiplayer_modes.offlinecoopmax',
    'multiplayer_modes.onlinecoop',
    'multiplayer_modes.onlinecoopmax',
    'multiplayer_modes.offlinemax',
    'multiplayer_modes.onlinemax',
    'screenshots.url',
    'videos.video_id',
    'websites.url',
    'url',
  ].join(',')
}

function buildSearchQuery(title: string) {
  const escaped = title.replace(/"/g, '\\"')
  return [
    `fields ${sharedFields()};`,
    `search "${escaped}";`,
    'where version_parent = null;',
    'limit 12;',
  ].join(' ')
}

function buildSlugQuery(slug: string) {
  const escaped = slug.replace(/"/g, '\\"')
  return [
    `fields ${sharedFields()};`,
    `where slug = "${escaped}" & version_parent = null;`,
    'limit 1;',
  ].join(' ')
}

function buildIdQuery(id: string) {
  return [
    `fields ${sharedFields()};`,
    `where id = ${Number(id)};`,
    'limit 1;',
  ].join(' ')
}

async function fetchIgdb(query: string, token: IgdbTokenResponse) {
  const igdbResponse = await fetch('https://api.igdb.com/v4/games', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Client-ID': TWITCH_CLIENT_ID,
      Authorization: `Bearer ${token.access_token}`,
    },
    body: query,
  })

  if (!igdbResponse.ok) {
    const details = await igdbResponse.text()
    throw new Error(`IGDB request failed: ${igdbResponse.status} ${details}`)
  }

  return await igdbResponse.json()
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
  const slug = (searchParams.get('slug') || '').trim()
  const id = (searchParams.get('id') || '').trim()
  if (!title && !slug && !id) {
    return json({ error: 'Missing title, slug, or id query parameter' }, 400)
  }

  try {
    const token = await getAccessToken()
    let queryType = 'title'
    let queryValue = title
    let query = buildSearchQuery(title)

    if (id) {
      queryType = 'id'
      queryValue = id
      query = buildIdQuery(id)
    } else if (slug) {
      queryType = 'slug'
      queryValue = slug
      query = buildSlugQuery(slug)
    }

    const results = await fetchIgdb(query, token)
    return json({ queryType, query: queryValue, results })
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
