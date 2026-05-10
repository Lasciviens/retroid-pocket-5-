(function(){
  const STORAGE_KEY='rp5_igdb_proxy_url';
  const DEFAULT_PROXY_URL='https://bniqmxbtvgwkaoswugds.supabase.co/functions/v1/igdb-search';

  function getProxyUrl(){
    const configured=(window.RP5_IGDB && window.RP5_IGDB.proxyUrl) || '';
    return (configured || localStorage.getItem(STORAGE_KEY) || DEFAULT_PROXY_URL || '').trim();
  }

  function getHeaders(){
    return { ...((window.RP5_IGDB && window.RP5_IGDB.headers) || {}) };
  }

  function setProxyUrl(url){
    const clean=(url||'').trim();
    if(clean){
      localStorage.setItem(STORAGE_KEY,clean);
    }else{
      localStorage.removeItem(STORAGE_KEY);
    }
    return clean;
  }

  function clearProxyUrl(){
    localStorage.removeItem(STORAGE_KEY);
  }

  function buildFallbackUrl(title){
    return `https://www.google.com/search?q=${encodeURIComponent(`site:igdb.com/games ${title}`)}`;
  }

  function buildGameUrl(slug){
    return slug?`https://www.igdb.com/games/${slug}`:'';
  }

  function extractRef(value){
    const raw=(value||'').trim();
    if(!raw)return null;
    if(/^\d+$/.test(raw)) return { type:'id', value:raw };
    if(raw.includes('igdb.com')){
      try{
        const url=new URL(raw);
        const parts=url.pathname.split('/').filter(Boolean);
        const gameIdx=parts.findIndex(part=>part==='games');
        if(gameIdx>=0 && parts[gameIdx+1]){
          return { type:'slug', value:parts[gameIdx+1] };
        }
      }catch(_error){}
    }
    if(/^[a-z0-9-]+$/i.test(raw) && raw.includes('-')){
      return { type:'slug', value:raw.toLowerCase() };
    }
    return null;
  }

  function normalizeCover(url){
    if(!url)return '';
    const full=url.startsWith('//')?`https:${url}`:url;
    return full.replace('/t_thumb/','/t_cover_big/');
  }

  function normalizeList(value,mapper){
    if(!Array.isArray(value))return [];
    return value.map(mapper).filter(Boolean);
  }

  function normalizeItem(item){
    const releaseTs=item.first_release_date || item.releaseDate || item.release_date || null;
    const releaseYear=releaseTs ? new Date(releaseTs * 1000).getFullYear() : (item.year || null);
    const companyRows=Array.isArray(item.involved_companies) ? item.involved_companies : [];
    const companies=normalizeList(companyRows.length ? companyRows : (item.companies || []), entry=>{
      if(typeof entry==='string')return entry;
      return entry.company?.name || entry.name || '';
    });
    const developers=normalizeList(companyRows, entry=>entry.developer ? (entry.company?.name || entry.name || '') : '');
    const publishers=normalizeList(companyRows, entry=>entry.publisher ? (entry.company?.name || entry.name || '') : '');
    const franchises=normalizeList(item.franchises || item.franchise, entry=>typeof entry==='string'?entry:(entry.name || ''));
    const collections=normalizeList(item.collections || item.collection, entry=>typeof entry==='string'?entry:(entry.name || ''));
    const themes=normalizeList(item.themes, entry=>typeof entry==='string'?entry:(entry.name || ''));
    const keywords=normalizeList(item.keywords, entry=>typeof entry==='string'?entry:(entry.name || ''));
    const screenshots=normalizeList(item.screenshots, entry=>normalizeCover(entry?.url || entry?.image_id || ''));
    const videos=normalizeList(item.videos, entry=>{
      const videoId=entry?.video_id || entry?.id || '';
      return videoId ? `https://www.youtube.com/watch?v=${videoId}` : '';
    });
    const websites=normalizeList(item.websites, entry=>entry?.url || '');
    const multiplayerModes=Array.isArray(item.multiplayer_modes) ? item.multiplayer_modes : [];
    const multiplayerSignals=[];
    multiplayerModes.forEach(mode=>{
      if(mode?.offlinecoop) multiplayerSignals.push(`Offline co-op${mode.offlinecoopmax?` (${mode.offlinecoopmax})`:''}`);
      if(mode?.onlinecoop) multiplayerSignals.push(`Online co-op${mode.onlinecoopmax?` (${mode.onlinecoopmax})`:''}`);
      if(mode?.offlinemax) multiplayerSignals.push(`Offline max ${mode.offlinemax}`);
      if(mode?.onlinemax) multiplayerSignals.push(`Online max ${mode.onlinemax}`);
    });
    const summary=item.summary || '';
    const storyline=item.storyline || '';
    const combinedSummary=[summary, storyline ? `Storyline: ${storyline}` : ''].filter(Boolean).join('\n\n');

    return {
      id:item.id || null,
      name:item.name || item.title || 'Bilinmeyen oyun',
      slug:item.slug || item.seo_slug || '',
      summary,
      storyline,
      combinedSummary:combinedSummary || item.description || '',
      rating:item.total_rating ?? item.rating ?? null,
      ratingCount:item.total_rating_count ?? item.rating_count ?? null,
      releaseYear,
      firstReleaseDate:releaseTs,
      coverUrl:normalizeCover(item.cover?.url || item.coverUrl || item.cover_url || ''),
      genres:normalizeList(item.genres, entry=>typeof entry==='string'?entry:(entry.name || '')),
      themes,
      keywords,
      platforms:normalizeList(item.platforms, entry=>typeof entry==='string'?entry:(entry.abbreviation || entry.name || '')),
      companies,
      developers,
      publishers,
      franchises,
      collections,
      screenshots,
      videos,
      websites,
      multiplayerSignals,
      igdbUrl:item.url || buildGameUrl(item.slug || item.seo_slug || '')
    };
  }

  function extractItems(payload){
    if(Array.isArray(payload))return payload;
    if(Array.isArray(payload.results))return payload.results;
    if(Array.isArray(payload.data))return payload.data;
    if(Array.isArray(payload.games))return payload.games;
    return [];
  }

  async function searchGames(title){
    const query=(title||'').trim();
    if(!query)return {status:'empty',query:'',results:[],fallbackUrl:''};

    const proxyUrl=getProxyUrl();
    if(!proxyUrl){
      return {status:'unconfigured',query,results:[],fallbackUrl:buildFallbackUrl(query)};
    }

    try{
      const glue=proxyUrl.includes('?')?'&':'?';
      const response=await fetch(`${proxyUrl}${glue}title=${encodeURIComponent(query)}`,{
        headers:{Accept:'application/json', ...getHeaders()}
      });
      if(!response.ok){
        return {status:'http_error',query,results:[],fallbackUrl:buildFallbackUrl(query),code:response.status};
      }
      const payload=await response.json();
      const results=extractItems(payload).map(normalizeItem).filter(item=>item.name);
      return {status:'ok',query,results,fallbackUrl:buildFallbackUrl(query),raw:payload};
    }catch(error){
      return {status:'network_error',query,results:[],fallbackUrl:buildFallbackUrl(query),error:String(error)};
    }
  }

  async function fetchByRef(refInput){
    const ref=typeof refInput === 'string' ? extractRef(refInput) : refInput;
    if(!ref || !ref.type || !ref.value){
      return {status:'invalid_ref',results:[]};
    }
    const proxyUrl=getProxyUrl();
    if(!proxyUrl){
      return {status:'unconfigured',results:[]};
    }
    try{
      const glue=proxyUrl.includes('?')?'&':'?';
      const response=await fetch(`${proxyUrl}${glue}${ref.type}=${encodeURIComponent(ref.value)}`,{
        headers:{Accept:'application/json', ...getHeaders()}
      });
      if(!response.ok){
        return {status:'http_error',results:[],code:response.status};
      }
      const payload=await response.json();
      const results=extractItems(payload).map(normalizeItem).filter(item=>item.name);
      return {status:'ok',results,raw:payload,ref};
    }catch(error){
      return {status:'network_error',results:[],error:String(error),ref};
    }
  }

  function normalizeText(value){
    return (value || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .replace(/[^a-z0-9]+/g,' ')
      .trim();
  }

  function uniqueList(values){
    return [...new Set((values || []).filter(Boolean))];
  }

  function choosePrimaryPlatform(platforms, preferredPlatform){
    if(preferredPlatform && platforms.includes(preferredPlatform)) return preferredPlatform;
    return platforms[0] || '';
  }

  function toNormalizedPayload(item, options={}){
    const normalizePlatformName=options.normalizePlatformName || (value=>value);
    const normalizedPlatforms=uniqueList((item.platforms || []).map(normalizePlatformName).filter(Boolean));
    const primaryPlatform=choosePrimaryPlatform(normalizedPlatforms, options.preferredPlatform || '');

    return {
      canonical_game: {
        title: item.name || '',
        normalized_title: normalizeText(item.name || ''),
        summary: item.summary || '',
        storyline: item.storyline || '',
        developer: item.developers?.[0] || item.companies?.[0] || '',
        publisher: item.publishers?.[0] || '',
        franchise: item.franchises?.[0] || '',
        collection: item.collections?.[0] || '',
        genres: uniqueList(item.genres || []),
        themes: uniqueList(item.themes || []),
        keywords: uniqueList(item.keywords || []),
        websites: uniqueList(item.websites || []),
        screenshots: uniqueList(item.screenshots || []),
        videos: uniqueList(item.videos || []),
        multiplayer_signals: uniqueList(item.multiplayerSignals || []),
      },
      platform_variants: normalizedPlatforms.map(platform=>({
        platform,
        igdb_game_id: item.id || null,
        igdb_slug: item.slug || '',
        igdb_url: item.igdbUrl || '',
        release_year: item.releaseYear || null,
        first_release_date: item.firstReleaseDate || null,
        rating: item.rating ?? null,
        rating_count: item.ratingCount ?? null,
        cover_url: item.coverUrl || '',
        multiplayer_signals: uniqueList(item.multiplayerSignals || []),
        version_title: item.name || '',
        is_primary_variant: platform === primaryPlatform,
      })),
      raw_igdb: {
        id: item.id || null,
        slug: item.slug || '',
        url: item.igdbUrl || buildGameUrl(item.slug || ''),
      },
    };
  }

  function scoreMatch(query, item, expectedYear){
    const queryNorm=normalizeText(query);
    const nameNorm=normalizeText(item?.name || '');
    if(!queryNorm || !nameNorm)return 0;

    let score=0;
    if(queryNorm===nameNorm)score+=82;
    else if(nameNorm.startsWith(queryNorm) || queryNorm.startsWith(nameNorm))score+=58;
    else if(nameNorm.includes(queryNorm) || queryNorm.includes(nameNorm))score+=44;

    const queryTokens=queryNorm.split(' ').filter(Boolean);
    const nameTokenList=nameNorm.split(' ').filter(Boolean);
    const nameTokens=new Set(nameTokenList);
    const tokenHits=queryTokens.filter(token=>nameTokens.has(token)).length;
    if(queryTokens.length){
      score+=Math.round((tokenHits / queryTokens.length) * 12);
    }

    if(queryNorm!==nameNorm){
      const extraTokens=Math.max(0, nameTokenList.length - queryTokens.length);
      score-=extraTokens * 8;
    }

    const itemYear=item?.releaseYear || null;
    if(expectedYear && itemYear){
      const diff=Math.abs(Number(expectedYear) - Number(itemYear));
      if(diff===0)score+=22;
      else if(diff===1)score+=14;
      else if(diff<=3)score+=6;
      else if(diff<=8)score-=10;
      else score-=22;
    }

    return Math.max(0, Math.min(100, score));
  }

  window.rp5IgdbBridge={
    getProxyUrl,
    getHeaders,
    setProxyUrl,
    clearProxyUrl,
    buildFallbackUrl,
    buildGameUrl,
    extractRef,
    searchGames,
    fetchByRef,
    scoreMatch,
    toNormalizedPayload
  };
})();
