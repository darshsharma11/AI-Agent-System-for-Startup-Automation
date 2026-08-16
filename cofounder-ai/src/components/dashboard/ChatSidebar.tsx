"use client";

import React from 'react';

export default function ChatSidebar() {
  return (
    <div className="w-[400px] h-full flex flex-col bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] border border-black/5 overflow-hidden ml-6">
      
      {/* Tabs */}
      <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-black/5 text-sm">
        <button className="bg-black/5 text-ink font-semibold px-4 py-1.5 rounded-full">Home</button>
        <button className="text-ink/60 hover:text-ink font-medium px-2 py-1.5 transition-colors">Company</button>
        <button className="text-ink/60 hover:text-ink font-medium px-2 py-1.5 transition-colors">Cofounder</button>
        <button className="text-ink/60 hover:text-ink font-medium px-2 py-1.5 transition-colors">Tasks</button>
        <button className="text-ink/60 hover:text-ink font-medium px-2 py-1.5 transition-colors">Library</button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        
        {/* User Message Card */}
        <div className="bg-paper border border-black/5 p-4 rounded-xl shadow-sm text-sm text-ink/80 leading-relaxed font-medium">
          Let's reach out to potential customers to validate our idea further.
        </div>

        {/* AI Response */}
        <div className="flex items-start space-x-3 pl-1">
          <div className="flex-shrink-0 pt-1">
            {/* Small icon for AI */}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-ink/40">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="9" y1="9" x2="15" y2="9"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
          </div>
          <div className="text-sm text-ink/60 leading-relaxed">
            That's a great way to make sure we're building the right features. I'm building a targeted list based on your ICP — LinkedIn activity, hiring signals, the kinds of things that tell us who's actually ready to buy right now. Once we have the right people, Sales will personalise an email for each one. <strong className="text-ink font-semibold">I'll bring you the emails to approve before anything sends.</strong>
          </div>
        </div>
        
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-black/5 bg-white">
        <div className="relative">
          <input 
            type="text" 
            placeholder="Ask cofounder to spin up new tasks agents..."
            className="w-full bg-paper border border-black/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brandBlue/20 text-ink placeholder:text-ink/30 pr-12 transition-all"
          />
          <button className="absolute right-2 top-1/2 -translate-y-1/2 bg-ink text-white w-8 h-8 rounded-lg flex items-center justify-center hover:bg-ink/80 transition-colors">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 19V5M5 12l7-7 7 7"/>
            </svg>
          </button>
        </div>
      </div>

    </div>
  );
}
