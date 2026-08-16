"use client";

import React from 'react';
import { motion } from 'framer-motion';

const AGENTS = [
  { name: 'Legal', angle: -90 },
  { name: 'Finance', angle: -45 },
  { name: 'Marketing', angle: 0 },
  { name: 'Support', angle: 45 },
  { name: 'Engineering', angle: 90 },
  { name: 'Operations', angle: 135 },
  { name: 'Design', angle: 180 },
  { name: 'Sales', angle: 225 },
];

export default function AgentGraph() {
  const radius = 220; // Distance from center

  return (
    <div className="relative w-full h-full min-h-[600px] flex items-center justify-center bg-paper/50 rounded-2xl border border-black/5 overflow-hidden shadow-inner">
      {/* Top Left Pills */}
      <div className="absolute top-4 left-4 flex space-x-2">
        <div className="bg-black/5 border border-black/10 px-3 py-1.5 rounded-md flex items-center space-x-2 text-xs font-medium text-ink/70">
          <span className="bg-black/10 rounded-full w-5 h-5 flex items-center justify-center text-[10px]">89</span>
          <span>General Intelligence... </span>
          <span className="text-[10px]">▼</span>
        </div>
        <div className="bg-transparent text-ink/40 text-xs font-medium px-2 py-1.5 flex items-center">
          Z 60%
        </div>
      </div>

      {/* Top Right Icons */}
      <div className="absolute top-6 right-6 flex space-x-4 text-ink/40">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" /></svg>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
      </div>

      {/* Graph Area */}
      <div className="relative w-[600px] h-[600px] flex items-center justify-center">
        {/* SVG for connections */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          <circle cx="300" cy="300" r={radius} className="stroke-black/5" strokeWidth="1" strokeDasharray="4 4" fill="none" />
          {AGENTS.map((agent, i) => {
            const rad = (agent.angle * Math.PI) / 180;
            const x = 300 + Math.cos(rad) * radius;
            const y = 300 + Math.sin(rad) * radius;
            return (
              <line 
                key={`line-${i}`}
                x1="300" 
                y1="300" 
                x2={x} 
                y2={y} 
                className="stroke-black/10" 
                strokeWidth="1" 
                strokeDasharray="4 4" 
              />
            );
          })}
        </svg>

        {/* Center Node */}
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute z-10 w-28 h-12 bg-white rounded-xl shadow-sm border border-black/5 flex flex-col items-center justify-center space-y-1"
        >
          <span className="text-sm">🌻</span>
          <span className="text-sm font-medium text-ink">Cofounder</span>
        </motion.div>

        {/* Outer Nodes */}
        {AGENTS.map((agent, i) => {
          const rad = (agent.angle * Math.PI) / 180;
          const x = Math.cos(rad) * radius;
          const y = Math.sin(rad) * radius;
          
          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, x: 0, y: 0 }}
              animate={{ opacity: 1, x, y }}
              transition={{ delay: i * 0.1 + 0.2 }}
              className="absolute z-10"
            >
              <div className="w-24 h-10 bg-white rounded-lg shadow-sm border border-black/5 flex items-center justify-center text-xs text-ink/70 font-medium">
                {agent.name}
              </div>
              
              {/* Fake children for visual fidelity based on screenshot */}
              {['Sales', 'Engineering', 'Marketing'].includes(agent.name) && (
                 <div className="absolute top-1/2 -translate-y-1/2 w-[120px] flex justify-between pointer-events-none" style={{
                   [agent.angle < -90 || agent.angle > 90 ? 'right' : 'left']: '110%'
                 }}>
                   <div className="w-8 h-[1px] bg-black/10 self-center" />
                   <div className="w-10 h-6 bg-black/5 rounded flex-shrink-0" />
                   <div className="w-10 h-6 bg-black/5 rounded flex-shrink-0 ml-2" />
                 </div>
              )}
            </motion.div>
          );
        })}
      </div>
      
      {/* Bottom text */}
      <div className="absolute bottom-4 left-4 text-[10px] text-ink/40 font-mono uppercase">
        ⚑ General intelligence company//superoptimizers
      </div>
    </div>
  );
}
