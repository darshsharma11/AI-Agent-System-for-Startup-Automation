"use client";

import React from 'react';
import AgentGraph from '@/components/dashboard/AgentGraph';
import ChatSidebar from '@/components/dashboard/ChatSidebar';
import { motion } from 'framer-motion';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-paper pt-24 pb-8 px-6 md:px-12">
      <div className="max-w-[1400px] mx-auto h-[calc(100vh-120px)]">
        
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col lg:flex-row h-full"
        >
          {/* Main Visual Canvas */}
          <div className="flex-1 min-w-0 bg-white rounded-2xl shadow-sm border border-black/5 overflow-hidden">
             <AgentGraph />
          </div>

          {/* Chat Sidebar */}
          <div className="hidden lg:block w-[400px] flex-shrink-0 h-full">
            <ChatSidebar />
          </div>
          
        </motion.div>
      </div>
    </div>
  );
}
