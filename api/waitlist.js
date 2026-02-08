export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", ["POST"]);
    return res.status(405).json({ ok: false, error: "Method not allowed" });
  }

  let payload = {};
  try {
    if (typeof req.body === "string") {
      try {
        payload = JSON.parse(req.body);
      } catch (err) {
        const params = new URLSearchParams(req.body);
        payload = Object.fromEntries(params.entries());
      }
    } else {
      payload = req.body;
    }
  } catch (err) {
    return res.status(400).json({ ok: false, error: "Invalid payload" });
  }

  const { email, saas_url: saasUrl } = payload || {};
  if (!email || !saasUrl) {
    return res.status(400).json({ ok: false, error: "Missing fields" });
  }

  const supabaseUrl = process.env.SUPABASE_URL;
  const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  const tableName = process.env.SUPABASE_TABLE || "waitlist";

  if (!supabaseUrl || !supabaseKey) {
    return res.status(500).json({
      ok: false,
      error: "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured"
    });
  }

  try {
    const response = await fetch(`${supabaseUrl}/rest/v1/${tableName}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: supabaseKey,
        Authorization: `Bearer ${supabaseKey}`,
        Prefer: "return=minimal"
      },
      body: JSON.stringify({
        email,
        saas_url: saasUrl,
        source: "waitlist"
      })
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(502).json({
        ok: false,
        error: "Supabase insert failed",
        detail: text.slice(0, 300)
      });
    }
  } catch (err) {
    return res.status(502).json({ ok: false, error: "Supabase insert failed" });
  }

  return res.status(200).json({ ok: true });
}
