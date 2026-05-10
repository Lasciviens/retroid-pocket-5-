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
    const companies=normalizeList(item.involved_companies || item.companies, entry=>{
      if(typeof entry==='string')return entry;
      return entry.company?.name || entry.name || '';
    });

    return {
      id:item.id || null,
      name:item.name || item.title || 'Bilinmeyen oyun',
      slug:item.slug || item.seo_slug || '',
      summary:item.summary || item.storyline || item.description || '',
      rating:item.total_rating ?? item.rating ?? null,
      releaseYear,
      coverUrl:normalizeCover(item.cover?.url || item.coverUrl || item.cover_url || ''),
      genres:normalizeList(item.genres, entry=>typeof entry==='string'?entry:(entry.name || '')),
      platforms:normalizeList(item.platforms, entry=>typeof entry==='string'?entry:(entry.abbreviation || entry.name || '')),
      companies,
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

  function normalizeText(value){
    return (value || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g,'')
      .replace(/[^a-z0-9]+/g,' ')
      .trim();
  }

  function scoreMatch(query, item, expectedYear){
    const queryNorm=normalizeText(query);
    const nameNorm=normalizeText(item?.name || '');
    if(!queryNorm || !nameNorm)return 0;

    let score=0;
    if(queryNorm===nameNorm)score+=78;
    else if(nameNorm.startsWith(queryNorm) || queryNorm.startsWith(nameNorm))score+=66;
    else if(nameNorm.includes(queryNorm) || queryNorm.includes(nameNorm))score+=54;

    const queryTokens=queryNorm.split(' ').filter(Boolean);
    const nameTokens=new Set(nameNorm.split(' ').filter(Boolean));
    const tokenHits=queryTokens.filter(token=>nameTokens.has(token)).length;
    if(queryTokens.length){
      score+=Math.round((tokenHits / queryTokens.length) * 25);
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
    searchGames,
    scoreMatch
  };
})();
