"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export default function Navbar() {
  const pathname = usePathname();
  const isHome = pathname === '/';

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4">
      {/* Logo */}
      <div className="flex-shrink-0">
        <Link 
          href="/" 
          className={twMerge(
            "text-2xl font-serif tracking-tight",
            isHome ? "text-white" : "text-ink"
          )}
        >
          Cofounder
        </Link>
      </div>

      {/* Center Navigation Pill */}
      <div className={twMerge(
        "hidden md:flex items-center justify-center space-x-6 backdrop-blur-md border px-6 py-2.5 rounded-full text-sm font-medium shadow-sm transition-colors",
        isHome ? "bg-white/10 border-white/20 text-white" : "bg-white/20 border-black/10 text-ink"
      )}>
        <Link href="#" className="opacity-70 hover:opacity-100 transition-opacity">How to</Link>
        <span className="opacity-30">|</span>
        <Link href="#" className={isHome ? "font-semibold text-white" : "font-semibold text-ink"}>Start</Link>
        <span className="opacity-30">|</span>
        <Link href="#" className="opacity-70 hover:opacity-100 transition-opacity">Build</Link>
        <span className="opacity-30">|</span>
        <Link href="#" className="opacity-70 hover:opacity-100 transition-opacity">Sell</Link>
        <span className="opacity-30">|</span>
        <Link href="#" className="opacity-70 hover:opacity-100 transition-opacity">Scale</Link>
      </div>

      {/* Right Navigation */}
      <div className="flex items-center space-x-4">
        <div className={twMerge(
          "hidden lg:flex items-center space-x-2 backdrop-blur-md border px-4 py-2 rounded-full text-sm font-medium shadow-sm transition-colors",
          isHome ? "bg-white/10 border-white/20 text-white" : "bg-white/20 border-black/10 text-ink"
        )}>
           <Link href="#" className="hover:opacity-70 transition-opacity">Resources</Link>
        </div>
        <div className={twMerge(
          "hidden lg:flex items-center space-x-2 backdrop-blur-md border px-4 py-2 rounded-full text-sm font-medium shadow-sm transition-colors",
          isHome ? "bg-white/10 border-white/20 text-white" : "bg-white/20 border-black/10 text-ink"
        )}>
           <Link href="#" className="hover:opacity-70 transition-opacity">Pricing</Link>
        </div>
        
        <Link 
          href="/dashboard" 
          className={twMerge(
            "px-5 py-2.5 rounded-xl text-sm font-semibold shadow-md transition-colors",
            isHome ? "bg-white text-ink hover:bg-white/90" : "bg-ink text-paper hover:bg-ink/90"
          )}
        >
          Run a company
        </Link>
      </div>
    </nav>
  );
}
