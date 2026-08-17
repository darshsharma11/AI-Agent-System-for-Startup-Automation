"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function OnboardingPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    industry: "",
    icp: "",
    brand_voice: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/companies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Failed to create company");
        setLoading(false);
        return;
      }

      // Redirect to main app
      router.push("/app");
    } catch (err) {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-brandBlue to-[#4595e6] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-ink mb-2">Welcome to Cofounder AI</h1>
            <p className="text-ink/60">Tell us about your company to get started</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label htmlFor="name" className="block text-sm font-medium text-ink mb-2">
                Company Name
              </label>
              <input
                id="name"
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 border border-ink/20 rounded-lg focus:ring-2 focus:ring-brandBlue focus:border-transparent outline-none transition"
                placeholder="Acme Inc"
              />
            </div>

            <div>
              <label htmlFor="industry" className="block text-sm font-medium text-ink mb-2">
                Industry
              </label>
              <input
                id="industry"
                type="text"
                required
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-3 border border-ink/20 rounded-lg focus:ring-2 focus:ring-brandBlue focus:border-transparent outline-none transition"
                placeholder="e.g. SaaS, E-commerce, Fintech"
              />
            </div>

            <div>
              <label htmlFor="icp" className="block text-sm font-medium text-ink mb-2">
                Ideal Customer Profile (ICP)
              </label>
              <textarea
                id="icp"
                required
                rows={3}
                value={formData.icp}
                onChange={(e) => setFormData({ ...formData, icp: e.target.value })}
                className="w-full px-4 py-3 border border-ink/20 rounded-lg focus:ring-2 focus:ring-brandBlue focus:border-transparent outline-none transition resize-none"
                placeholder="Describe your ideal customer (e.g., B2B SaaS founders, small businesses, etc.)"
              />
            </div>

            <div>
              <label htmlFor="brand_voice" className="block text-sm font-medium text-ink mb-2">
                Brand Voice
              </label>
              <textarea
                id="brand_voice"
                required
                rows={3}
                value={formData.brand_voice}
                onChange={(e) => setFormData({ ...formData, brand_voice: e.target.value })}
                className="w-full px-4 py-3 border border-ink/20 rounded-lg focus:ring-2 focus:ring-brandBlue focus:border-transparent outline-none transition resize-none"
                placeholder="Describe your brands tone and voice (e.g., Professional yet approachable, Fun and energetic, etc.)"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-brandBlue text-white py-3 rounded-lg font-semibold hover:bg-brandBlue/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Setting up..." : "Complete setup"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
