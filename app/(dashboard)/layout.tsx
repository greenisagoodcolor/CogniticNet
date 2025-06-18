import { NavBar } from '@/components/nav-bar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <NavBar />
      <main className="pt-16">
        {children}
      </main>
    </div>
  );
} 