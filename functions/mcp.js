// POST /mcp — Model Context Protocol server (streamable HTTP, stateless).
// Exposes one tool: ask_the_book(question) — answers strictly from the text of
// The Working Upholsterer's Bible at learntoupholster.com.
// Requires secret: ANTHROPIC_API_KEY (already set for /api/ask).

let INDEX = null;

const STOP = new Set(('a an and are as at be but by can do does for from how i in is it its of on or ' +
  'that the this to was what when where which why will with you your me my how much many need').split(' '));
const tokens = s => (s.toLowerCase().match(/[a-z][a-z'-]{1,}/g) || []).filter(w => !STOP.has(w));

function retrieve(index, question, n) {
  const q = tokens(question);
  if (!q.length) return [];
  return index.map(c => {
    const body = c.x.toLowerCase(), head = (c.t + ' ' + c.h).toLowerCase();
    let s = 0;
    for (const w of q) {
      let i = -1, tf = 0;
      while ((i = body.indexOf(w, i + 1)) !== -1 && tf < 6) tf++;
      s += tf;
      if (head.includes(w)) s += 4;
    }
    return [s, c];
  }).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, n).map(x => x[1]);
}

async function askTheBook(question, env, requestUrl) {
  question = String(question || '').trim().slice(0, 300);
  if (!question) return { text: 'Please provide a question.', isError: true };
  if (!INDEX) {
    const res = await env.ASSETS.fetch(new URL('/ask-index.json', requestUrl));
    if (!res.ok) return { text: 'Knowledge index unavailable.', isError: true };
    INDEX = await res.json();
  }
  const hits = retrieve(INDEX, question, 8);
  if (!hits.length) {
    return { text: "The book doesn't appear to cover that. Browse the contents at https://www.learntoupholster.com/contents" };
  }
  const excerpts = hits.map((c, i) => `[${i + 1}] From "${c.t}" (https://www.learntoupholster.com${c.u}), section "${c.h}":\n${c.x}`).join('\n\n');
  const system = `You are the MCP tool for learntoupholster.com — the free online edition of "The Working Upholsterer's Bible" by Shaun Greenwood, master upholsterer. Answer using ONLY the numbered excerpts provided. If they don't cover the question, say the book doesn't cover it. British English, plain prose, concise (2–6 sentences). End with the most relevant source URL on its own line. Never contradict the UK Furniture & Furnishings (Fire) (Safety) Regulations.`;
  const apiRes = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY, 'anthropic-version': '2023-06-01' },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001', max_tokens: 500, system,
      messages: [{ role: 'user', content: `Excerpts from the book:\n\n${excerpts}\n\nQuestion: ${question}` }]
    })
  });
  if (!apiRes.ok) return { text: 'The assistant is temporarily unavailable — please try again.', isError: true };
  const data = await apiRes.json();
  const answer = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();
  return { text: answer };
}

const TOOLS = [{
  name: 'ask_the_book',
  title: 'Ask The Working Upholsterer\u2019s Bible',
  description: 'Ask a practical upholstery question and get an answer grounded strictly in the text of The Working Upholsterer\u2019s Bible by Shaun Greenwood (master upholsterer, AMUSF accredited) \u2014 traditional and modern techniques, materials, UK fire regulations, projects and pricing. Answers cite the source chapter URL on learntoupholster.com.',
  inputSchema: {
    type: 'object',
    properties: { question: { type: 'string', description: 'The upholstery question, in plain English (max 300 characters).' } },
    required: ['question']
  }
}];

const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-methods': 'POST, OPTIONS',
  'access-control-allow-headers': 'content-type, accept, mcp-protocol-version, mcp-session-id'
};
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json', ...CORS } });
const rpcResult = (id, result) => json({ jsonrpc: '2.0', id, result });
const rpcError = (id, code, message, status = 200) => json({ jsonrpc: '2.0', id: id ?? null, error: { code, message } }, status);

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS });
}
export async function onRequestGet() {
  return json({ error: 'This is an MCP endpoint. Connect with an MCP client (streamable HTTP) and call the ask_the_book tool. Server card: /.well-known/mcp/server-card.json' }, 405);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  let msg;
  try { msg = await request.json(); } catch { return rpcError(null, -32700, 'Parse error', 400); }
  if (Array.isArray(msg)) return rpcError(null, -32600, 'Batching not supported', 400);
  const { id, method, params } = msg || {};
  if (!method) return rpcError(id, -32600, 'Invalid request', 400);

  // notifications (no id) get 202 Accepted
  if (id === undefined || id === null) {
    return new Response(null, { status: 202, headers: CORS });
  }

  switch (method) {
    case 'initialize': {
      const requested = params && params.protocolVersion;
      const supported = ['2025-06-18', '2025-03-26', '2024-11-05'];
      const version = supported.includes(requested) ? requested : '2025-06-18';
      return rpcResult(id, {
        protocolVersion: version,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: 'learntoupholster-ask-the-book', title: 'The Working Upholsterer\u2019s Bible', version: '1.0.0' },
        instructions: 'One tool: ask_the_book. Answers come only from the text of The Working Upholsterer\u2019s Bible (learntoupholster.com) and include a source chapter URL. Guidance on UK fire regulations is informational, not legal advice.'
      });
    }
    case 'ping':
      return rpcResult(id, {});
    case 'tools/list':
      return rpcResult(id, { tools: TOOLS });
    case 'tools/call': {
      const name = params && params.name;
      if (name !== 'ask_the_book') return rpcError(id, -32602, `Unknown tool: ${name}`);
      const q = params && params.arguments && params.arguments.question;
      const out = await askTheBook(q, env, request.url);
      return rpcResult(id, { content: [{ type: 'text', text: out.text }], isError: !!out.isError });
    }
    case 'resources/list':
      return rpcResult(id, { resources: [] });
    case 'prompts/list':
      return rpcResult(id, { prompts: [] });
    default:
      return rpcError(id, -32601, `Method not found: ${method}`);
  }
}
