// POST /api/ask  { question: "..." }
// Answers questions using ONLY the content of learntoupholster.com.
// Requires secret: ANTHROPIC_API_KEY
//   npx wrangler pages secret put ANTHROPIC_API_KEY --project-name=learntoupholster

let INDEX = null; // cached between invocations on a warm isolate

// Amazon Associates catalogue — deterministic matching, tag baked in.
const AFF_TAG = '842699-21';
const TOOLS = [
  { k: ['webbing strainer', 'webbing stretcher', 'tension webbing', 'strain the webbing'], label: 'Webbing strainer', q: 'webbing+stretcher+upholstery' },
  { k: ['jute webbing', 'webbing', 'elastic webbing'], label: 'Jute upholstery webbing', q: 'jute+upholstery+webbing' },
  { k: ['tack hammer', 'magnetic hammer', 'cabriole hammer', 'tacks'], label: 'Magnetic tack hammer', q: 'upholstery+tack+hammer' },
  { k: ['staple gun', 'staples', 'staple'], label: 'Upholstery staple gun', q: 'upholstery+staple+gun' },
  { k: ['ripping chisel', 'ripping down', 'strip the old', 'stripping'], label: 'Ripping chisel', q: 'ripping+chisel+upholstery' },
  { k: ['tack lifter', 'staple remover', 'staple lifter'], label: 'Tack &amp; staple lifter', q: 'upholstery+staple+remover+tack+lifter' },
  { k: ['scissors', 'shears', 'cutting fabric'], label: 'Upholstery shears', q: 'upholstery+scissors' },
  { k: ['leather scissors', 'cutting leather', 'skiving'], label: 'Leather scissors &amp; skiving knife', q: 'leather+scissors+skiving+knife' },
  { k: ['double-pointed needle', 'buttoning needle', 'mattress needle', 'stitching needle', 'blind stitch', 'top stitch', 'stitched edge'], label: 'Double-pointed stitching needles', q: 'upholstery+needles+double+pointed' },
  { k: ['curved needle', 'slip stitch', 'slipping'], label: 'Curved slipping needles', q: 'curved+upholstery+needles' },
  { k: ['twine', 'laid cord', 'lashing', 'lashing cord'], label: 'Upholstery twine &amp; laid cord', q: 'upholstery+twine+laid+cord' },
  { k: ['springs', 'coil spring', 'serpentine', 'zigzag spring'], label: 'Upholstery springs', q: 'upholstery+coil+springs' },
  { k: ['hessian', 'scrim'], label: 'Hessian / scrim', q: 'upholstery+hessian+10oz' },
  { k: ['horsehair', 'fibre stuffing', 'coir', 'stuffing'], label: 'Upholstery fibre stuffing', q: 'upholstery+fibre+stuffing+coir' },
  { k: ['calico'], label: 'Upholstery calico', q: 'upholstery+calico+fabric' },
  { k: ['wadding', 'dacron', 'polyester wrap', 'skin wadding'], label: 'Polyester wadding (Dacron)', q: 'upholstery+polyester+wadding' },
  { k: ['foam', 'cushion foam', 'seat pad'], label: 'CMHR upholstery foam', q: 'CMHR+upholstery+foam' },
  { k: ['spray adhesive', 'contact adhesive', 'glue'], label: 'Upholstery spray adhesive', q: 'upholstery+spray+adhesive' },
  { k: ['buttons', 'button press', 'covered buttons', 'buttoning', 'tufting'], label: 'Button-covering kit', q: 'upholstery+button+covering+kit' },
  { k: ['gimp', 'gimp pins', 'braid', 'trim'], label: 'Gimp, braid &amp; gimp pins', q: 'upholstery+gimp+braid' },
  { k: ['piping cord', 'piping', 'welt'], label: 'Piping cord', q: 'upholstery+piping+cord' },
  { k: ['tape measure', 'measuring', 'measure up', 'yardage'], label: 'Cloth tailor&#8217;s tape measure', q: 'cloth+tailors+tape+measure' },
  { k: ['tailors chalk', 'chalk', 'marking out'], label: 'Tailor&#8217;s chalk', q: 'tailors+chalk' },
  { k: ['sewing machine', 'walking foot', 'machine sewing'], label: 'Heavy-duty sewing machine', q: 'heavy+duty+sewing+machine+upholstery' },
  { k: ['cambric', 'bottoming cloth', 'dust cover'], label: 'Black bottoming cambric', q: 'upholstery+cambric+bottom+cloth' }
];

function matchTools(text, max) {
  const t = text.toLowerCase();
  const out = [];
  for (const tool of TOOLS) {
    if (tool.k.some(k => t.includes(k))) {
      out.push({ label: tool.label, url: `https://www.amazon.co.uk/s?k=${tool.q}&tag=${AFF_TAG}` });
      if (out.length >= max) break;
    }
  }
  return out;
}

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
  // affiliate tools relevant to the question and answer (deterministic, tag baked in)
  const tools = matchTools(question + ' ' + answer, 3);
  return json({ answer, sources, tools });
}
