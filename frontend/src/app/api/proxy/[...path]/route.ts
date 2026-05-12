import { NextRequest, NextResponse } from 'next/server';

const _raw = (
  process.env.BACKEND_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  'https://uganda-ai-learning-production.up.railway.app/api/v1'
).replace(/\/$/, '');

const BACKEND_BASE = _raw.endsWith('/api/v1') ? _raw : `${_raw}/api/v1`;

type Ctx = { params: { path: string[] } };

async function proxyRequest(req: NextRequest, ctx: Ctx): Promise<NextResponse> {
  const path = (ctx.params.path ?? []).join('/');
  const search = req.nextUrl.search;
  const targetUrl = `${BACKEND_BASE}/${path}/${search}`;

  const headers: Record<string, string> = {
    'content-type': 'application/json',
    accept: 'application/json',
  };

  const auth = req.headers.get('authorization');
  if (auth) headers.authorization = auth;

  let body: string | undefined;
  if (req.method !== 'GET' && req.method !== 'HEAD') {
    const text = await req.text();
    if (text) body = text;
  }

  try {
    const upstream = await fetch(targetUrl, {
      method: req.method,
      headers,
      body,
      cache: 'no-store',
    });
    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: {
        'content-type': upstream.headers.get('content-type') ?? 'application/json',
      },
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: 'Backend unreachable', detail: msg }, { status: 502 });
  }
}

export async function GET(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function POST(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function PUT(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function PATCH(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function DELETE(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
