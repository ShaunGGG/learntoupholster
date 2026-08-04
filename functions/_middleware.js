// Markdown content negotiation (Markdown for Agents, self-hosted).
// GET requests for pages with `Accept: text/markdown` receive the pre-built
// markdown variant from /md/<slug>.md as text/markdown; browsers get HTML as normal.

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;


  // ltu-our-work-retired
  // The gallery moved onto the projects page. Permanent redirect so inbound
  // links, bookmarks and search results keep working.
  if (path === '/our-work' || path === '/our-work/') {
    return Response.redirect(new URL('/projects/#gallery', request.url).toString(), 301);
  }
  // Internal workflow files: present in the repo, never served publicly.
  if (/\.(py|toml|sql|bak)$/i.test(path) || /^\/[^/]+\.md$/i.test(path) ||
      path.startsWith('/project-sources/') || path.startsWith('/business-sources/') ||
      path.startsWith('/outreach/') ||
      (path.startsWith('/.') && !path.startsWith('/.well-known/'))) {
    const nf = await env.ASSETS.fetch(new URL('/404.html', request.url));
    return new Response(nf.body, { status: 404, headers: { 'content-type': 'text/html; charset=utf-8' } });
  }

  // only page routes (no file extension), only GET
  const isPage = request.method === 'GET' && !/\.[a-z0-9]+$/i.test(path) && !path.startsWith('/api/') && path !== '/mcp';

  if (isPage) {
    const accept = request.headers.get('accept') || '';
    if (accept.includes('text/markdown')) {
      const slug = path === '/' ? 'index' : path.replace(/\/+$/, '').slice(1);
      const mdRes = await env.ASSETS.fetch(new URL('/md/' + slug + '.md', request.url));
      if (mdRes.ok) {
        const body = await mdRes.text();
        return new Response(body, {
          headers: {
            'content-type': 'text/markdown; charset=utf-8',
            'vary': 'Accept',
            'x-markdown-tokens': String(Math.ceil(body.length / 4)),
            'link': '<' + url.origin + path + '>; rel="canonical"'
          }
        });
      }
    }
    const res = await next();
    const out = new Response(res.body, res);
    out.headers.append('vary', 'Accept');
    return out;
  }
  return next();
}
