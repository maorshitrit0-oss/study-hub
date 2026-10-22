import Nav from "@/components/Nav";
import Credit from "@/components/Credit";
import TopBar from "@/components/TopBar";

export default function AppLayout({ children }: LayoutProps<"/">) {
  return (
    <>
      <main className="mx-auto max-w-3xl px-4 pt-[max(1rem,env(safe-area-inset-top))] pb-28">
        <TopBar />
        {children}
        <Credit className="mt-10" />
      </main>
      <Nav />
    </>
  );
}
