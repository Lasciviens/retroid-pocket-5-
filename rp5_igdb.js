(function(){
  const STORAGE_KEY='rp5_igdb_proxy_url';

  function getProxyUrl(){
    const configured=(window.RP5_IGDB && window.RP5_IGDB.proxyUrl) || '';
    return (configured || localStorage.getItem(STORAGE_KEY) || '').trim();
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
        headers:{Accept:'application/json'}
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

  window.rp5IgdbBridge={
    getProxyUrl,
    setProxyUrl,
    clearProxyUrl,
    buildFallbackUrl,
    buildGameUrl,
    searchGames
  };
})();
