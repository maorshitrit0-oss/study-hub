// Supabase (PostgREST) returns at most 1000 rows per request; quizzes pass that within a semester.
// fetchAll pages through a query. Pass a function that builds the query (it is rebuilt for each page).
type Page<T> = PromiseLike<{ data: T[] | null; error: unknown }>;
export async function fetchAll<T>(query: () => { range: (from: number, to: number) => Page<T> }, pageSize = 1000) {
  const rows: T[] = [];
  for (let from = 0; ; from += pageSize) {
    const { data, error } = await query().range(from, from + pageSize - 1);
    if (error) throw error;
    rows.push(...(data ?? []));
    if (!data || data.length < pageSize) return rows;
  }
}
