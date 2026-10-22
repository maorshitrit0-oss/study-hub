"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { supabaseServer } from "@/lib/supabase/server";

export type AuthState = { error?: string; message?: string };

export async function authenticate(_: AuthState, form: FormData): Promise<AuthState> {
  const email = String(form.get("email") || "").trim();
  const password = String(form.get("password") || "");
  const mode = form.get("mode");
  const sb = await supabaseServer();

  if (mode === "signup") {
    const origin = (await headers()).get("origin") ?? "";
    const { data, error } = await sb.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: `${origin}/auth/callback` },
    });
    if (error) return { error: translate(error.message) };
    if (!data.session) return { message: "נשלח אליך מייל אימות. לחץ על הקישור שבו ואז התחבר." };
  } else {
    const { error } = await sb.auth.signInWithPassword({ email, password });
    if (error) return { error: translate(error.message) };
  }
  redirect("/");
}

export async function signOut() {
  const sb = await supabaseServer();
  await sb.auth.signOut();
  redirect("/login");
}

function translate(msg: string) {
  if (/invalid login/i.test(msg)) return "אימייל או סיסמה שגויים";
  if (/already registered/i.test(msg)) return "המשתמש כבר קיים - התחבר במקום להירשם";
  if (/at least/i.test(msg)) return "הסיסמה קצרה מדי (לפחות 6 תווים)";
  if (/not confirmed/i.test(msg)) return "צריך לאשר את המייל קודם (בדוק את תיבת הדואר)";
  return msg;
}
