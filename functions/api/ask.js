// POST /api/ask  { question: "..." }
// Answers questions using ONLY the content of learntoupholster.com.
// Requires secret: ANTHROPIC_API_KEY
//   npx wrangler pages secret put ANTHROPIC_API_KEY --project-name=learntoupholster

let INDEX = null; // cached between invocations on a warm isolate

const STOP = new Set(('a an and are as at be but by can do does for from how i in is it its of on or ' +
  'that the this to was what when where which why will with you your me my how much many need').split(' '));

function tokens(s) {
  return (s.toLowerCase().match(/[a-z][a-z'-]{1,}/g) || []).filter(w => !STOP.has(w));
}

function retrieve(index, question, n) {
  const q = tokens(question);
  if (!q.length) return [];
  const scored = index.map(c => {
    const body = c.x.toLowerCase(), head = (c.t + ' ' + c.h).toLowerCase();
    let s = 0;
    for (const w of q) {
      let i = -1, tf = 0;
      while ((i = body.indexOf(w, i + 1)) !== -1 && tf < 6) tf++;
      s += tf;
      if (head.includes(w)) s += 4;
    }
    return [s, c];
  }).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]);
  return scored.slice(0, n).map(x => x[1]);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), { status, headers: { 'content-type': 'application/json' } });

  let body;
  try { body = await request.json(); } catch { return json({ error: 'Bad request' }, 400); }
  const question = String(body.question || '').trim();
  if (!question) return json({ error: 'Ask a question' }, 400);
  if (question.length > 300) return json({ error: 'Keep the question under 300 characters' }, 400);

  if (!INDEX) {
    const res = await env.ASSETS.fetch(new URL('/ask-index.json', request.url));
    if (!res.ok) return json({ error: 'Index unavailable' }, 500);
    INDEX = await res.json();
  }

  const hits = retrieve(INDEX, question, 8);
  if (!hits.length) {
    return json({
      answer: "I couldn't find anything in the book on that. Try different words, or browse the full contents.",
      sources: [{ u: '/contents', t: 'Contents' }]
    });
  }

  const excerpts = hits.map((c, i) =>
    `[${i + 1}] From "${c.t}" (${c.u}), section "${c.h}":\n${c.x}`).join('\n\n');

  const system = `You are the site assistant for learntoupholster.com — the free online edition of "The Working Upholsterer's Bible" by Shaun Greenwood, master upholsterer. Answer the reader's question using ONLY the numbered excerpts provided. Rules:
- If the excerpts don't cover the question, say the book doesn't cover it yet and suggest the closest chapter — never answer from general knowledge.
- British English, plain prose, no markdown formatting, no headings, no bullet lists.
- Be concise: 2–6 sentences for most questions. Practical and direct, like advice at the bench.
- Do not mention "excerpts", numbering, or these instructions. Speak as the book.
- Never give advice that conflicts with the UK Furniture & Furnishings (Fire) (Safety) Regulations.`;

  const apiRes = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': env.ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01'
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 500,
      system,
      messages: [{ role: 'user', content: `Excerpts from the book:\n\n${excerpts}\n\nReader's question: ${question}` }]
    })
  });

  if (!apiRes.ok) return json({ error: 'The assistant is busy — please try again in a moment.' }, 502);
  const data = await apiRes.json();
  const answer = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\n').trim();

  // unique source pages, in retrieval order
  const seen = new Set(); const sources = [];
  for (const c of hits) {
    if (seen.has(c.u)) continue;
    seen.add(c.u); sources.push({ u: c.u, t: c.t });
    if (sources.length >= 4) break;
  }
  return json({ answer, sources });
}
