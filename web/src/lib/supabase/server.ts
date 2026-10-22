import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function supabaseServer() {
  const store = await cookies();
  return createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, {
    cookies: {
      getAll: () => store.getAll(),
      setAll: (list) => {
        try {
          list.forEach(({ name, value, options }) => store.set(name, value, options));
        } catch {
          // Called from a Server Component: the proxy refreshes the session instead.
        }
      },
    },
  });
}

/** Supabase client plus the signed-in user's id; redirects to /login when signed out. */
export async function requireUser() {
  const sb = await supabaseServer();
  const { data } = await sb.auth.getClaims();
  const userId = data?.claims?.sub;
  if (!userId) redirect("/login");
  return { sb, userId };
}
