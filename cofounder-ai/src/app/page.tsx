"use client";

import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function Home() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#4595e6]">
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <Image 
          src="/pixel_art_landscape.jpg" 
          alt="Pixel Art Landscape" 
          fill
          priority
          className="object-cover object-bottom"
        />
        {/* Gradient overlay to make text more readable at top */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#14213D]/40 to-transparent h-1/2 z-10" />
      </div>

      {/* Main Content */}
      <div className="relative z-20 flex flex-col items-start justify-center h-screen max-w-7xl mx-auto px-6 sm:px-12 pt-20">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="max-w-2xl"
        >
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-white mb-6 leading-[1.1]">
            Cofounder lets you run an entire company with AI
          </h1>
          
          <p className="text-lg sm:text-xl text-white/90 font-medium mb-10 max-w-xl leading-relaxed">
            Start with an AI roadmap, then hand off engineering, sales, marketing, design, finance, and ops to agents.
          </p>

          <div className="flex flex-wrap items-center gap-4">
            <Link href="/signup" className="bg-white text-ink px-6 py-3 rounded-xl font-semibold hover:bg-paper transition-colors shadow-lg">
              Run a company
            </Link>
            <button className="bg-[#38bdf8]/80 backdrop-blur-sm text-white px-6 py-3 rounded-xl font-semibold hover:bg-[#38bdf8] transition-colors border border-white/20 shadow-lg">
              Check out the launch
            </button>
          </div>
        </motion.div>
      </div>

      {/* Floating Notifications */}
      <div className="absolute right-12 top-1/3 z-20 flex flex-col gap-4">
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          className="bg-black/40 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 flex items-center space-x-3 shadow-2xl"
        >
          <div className="w-2 h-2 rounded-full bg-green-400" />
          <span className="text-white/80 text-sm">Task Completed</span>
          <span className="text-white font-semibold text-sm">Marketing Campaign</span>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 1.2 }}
          className="bg-black/40 backdrop-blur-md border border-white/10 rounded-xl px-4 py-3 flex items-center space-x-3 shadow-2xl"
        >
          <div className="w-2 h-2 rounded-full bg-green-400" />
          <span className="text-white/80 text-sm">Task Completed</span>
          <span className="text-white font-semibold text-sm">New webpage</span>
        </motion.div>
      </div>
    </div>
  );
}
