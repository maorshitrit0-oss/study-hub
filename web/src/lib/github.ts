/** Starts a GitHub Actions workflow in the repo (processing runs there, for free). */
async function dispatch(workflow: string, inputs: Record<string, string>) {
  const repo = process.env.GITHUB_REPO;
  const token = process.env.GITHUB_TOKEN;
  if (!repo || !token) return "GITHUB_REPO / GITHUB_TOKEN לא מוגדרים ב-Vercel";
  const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/${workflow}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify({ ref: process.env.GITHUB_REF || "main", inputs }),
  });
  return res.ok ? null : `GitHub ${res.status}: ${(await res.text()).slice(0, 300)}`;
}

/** Download, transcribe and author a lesson. */
export const dispatchLesson = (lessonId: string, author: "gemini" | "none" = "gemini") =>
  dispatch("process.yml", { lesson_id: lessonId, author });

/** Push notifications: "setup" creates the signing keys, "test" pings one user. */
export const dispatchNotify = (mode: "setup" | "test", userId = "") =>
  dispatch("notify.yml", { mode, user_id: userId });

/** Podcast / video / everyday examples from lesson chapters (worker/studio.py). */
export const dispatchStudio = (mediaId: string) => dispatch("media.yml", { media_id: mediaId });
