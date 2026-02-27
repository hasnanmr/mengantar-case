"use client";
import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import ChatWindow from "@/components/ChatWindow";

export default function Home() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [sessionKey, setSessionKey] = useState(0);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleNewSession = () => {
    setActiveThreadId(null);
    setSessionKey((k) => k + 1);
  };

  const handleSelectThread = (id: string) => {
    setActiveThreadId(id);
    // We don't increment sessionKey here because we want to reuse the same ChatWindow 
    // and let its useEffect handle the history loading.
  };

  const toggleSidebar = () => setIsSidebarCollapsed((prev) => !prev);

  return (
    <div className="app-layout">
      <Sidebar
        activeThreadId={activeThreadId}
        onSelectThread={handleSelectThread}
        onNewSession={handleNewSession}
        isCollapsed={isSidebarCollapsed}
      />
      <ChatWindow
        key={sessionKey}
        threadId={activeThreadId}
        onThreadCreated={setActiveThreadId}
        isSidebarCollapsed={isSidebarCollapsed}
        onToggleSidebar={toggleSidebar}
      />
    </div>
  );
}
