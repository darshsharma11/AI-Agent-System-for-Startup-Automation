"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface UserData {
  email: string;
  company?: {
    name: string;
    industry: string;
  };
}

export default function AppPage() {
  const router = useRouter();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("/api/auth/me");
        if (!res.ok) {
          router.push("/login");
          return;
        }
        const data = await res.json();
        setUserData(data);
      } catch (err) {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="text-ink">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-paper">
      {/* Header */}
      <header className="bg-white border-b border-ink/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink">Cofounder AI</h1>
            {userData?.company && (
              <p className="text-sm text-ink/60">{userData.company.name}</p>
            )}
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm text-ink/60 hover:text-ink transition"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-white rounded-xl border border-ink/10 p-8">
          <h2 className="text-3xl font-bold text-ink mb-4">
            Welcome to your AI-powered workspace
          </h2>
          <p className="text-ink/60 mb-6">
            You're all set! This is where your AI agents will help you run your company.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-brandBlueSoft border border-brandBlue/20 rounded-lg p-6">
              <h3 className="font-semibold text-ink mb-2">Sales Agent</h3>
              <p className="text-sm text-ink/60">Manage leads and outreach sequences</p>
            </div>
            <div className="bg-brandGreenSoft border border-brandGreen/20 rounded-lg p-6">
              <h3 className="font-semibold text-ink mb-2">Marketing Agent</h3>
              <p className="text-sm text-ink/60">Create campaigns and content</p>
            </div>
            <div className="bg-watchOutSoft border border-watchOut/20 rounded-lg p-6">
              <h3 className="font-semibold text-ink mb-2">Support Agent</h3>
              <p className="text-sm text-ink/60">Handle customer inquiries</p>
            </div>
          </div>
        </div>

        {/* User Info */}
        {userData && (
          <div className="mt-6 bg-white rounded-xl border border-ink/10 p-6">
            <h3 className="font-semibold text-ink mb-3">Account Info</h3>
            <div className="space-y-2 text-sm">
              <p><span className="text-ink/60">Email:</span> <span className="text-ink font-medium">{userData.email}</span></p>
              {userData.company && (
                <>
                  <p><span className="text-ink/60">Company:</span> <span className="text-ink font-medium">{userData.company.name}</span></p>
                  <p><span className="text-ink/60">Industry:</span> <span className="text-ink font-medium">{userData.company.industry}</span></p>
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
