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

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);

  try {
    const upstream = await fetch(targetUrl, {
      method: req.method,
      headers,
      body,
      cache: 'no-store',
      signal: controller.signal,
    });

    clearTimeout(timer);

    const contentType = upstream.headers.get('content-type') ?? '';
    if (!contentType.includes('application/json') && !contentType.includes('text/plain')) {
      return NextResponse.json(
        { error: `Backend returned status ${upstream.status}`, detail: 'Backend may be down or starting up — please try again.' },
        { status: 502 }
      );
    }

    const text = await upstream.text();
    return new NextResponse(text, {
      status: upstream.status,
      headers: { 'content-type': 'application/json' },
    });
  } catch (err) {
    clearTimeout(timer);
    const msg = err instanceof Error ? err.message : String(err);
    const isTimeout = msg.includes('abort') || msg.includes('timeout');
    return NextResponse.json(
      {
        error: isTimeout ? 'Backend timed out' : 'Backend unreachable',
        detail: isTimeout
          ? 'The backend took too long to respond. It may be starting up — wait 30 seconds and try again.'
          : msg,
      },
      { status: 502 }
    );
  }
}

export async function GET(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function POST(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function PUT(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function PATCH(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
export async function DELETE(req: NextRequest, ctx: Ctx) { return proxyRequest(req, ctx); }
