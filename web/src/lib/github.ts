/** Starts the GitHub Actions workflow that downloads, transcribes and authors a lesson. */
export async function dispatchLesson(lessonId: string, author: "gemini" | "none" = "gemini") {
  const repo = process.env.GITHUB_REPO;
  const token = process.env.GITHUB_TOKEN;
  if (!repo || !token) return "GITHUB_REPO / GITHUB_TOKEN לא מוגדרים ב-Vercel";
  const res = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/process.yml/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
    body: JSON.stringify({ ref: process.env.GITHUB_REF || "main", inputs: { lesson_id: lessonId, author } }),
  });
  return res.ok ? null : `GitHub ${res.status}: ${(await res.text()).slice(0, 300)}`;
}
