import { NextRequest } from "next/server";
import { AccessToken } from "livekit-server-sdk";

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const username = url.searchParams.get("username") || "candidate";
  const room = url.searchParams.get("room") || "interview-room";

  const apiKey = process.env.LIVEKIT_API_KEY!;
  const apiSecret = process.env.LIVEKIT_API_SECRET!;

  const at = new AccessToken(apiKey, apiSecret, {
    identity: username,
  });
  at.addGrant({ roomJoin: true, room });

  const token = await at.toJwt();
  return new Response(token, { status: 200 });
}
