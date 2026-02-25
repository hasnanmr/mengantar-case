"use client";
import { useState } from "react";
import Sidebar from "@/components/Sidebar";
import ChatWindow from "@/components/ChatWindow";

export default function Home() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [sessionKey, setSessionKey] = useState(0);

  const handleNewSession = () => {
    setActiveThreadId(null);
    setSessionKey((k) => k + 1);
  };

  return (
    <div className="app-layout">
      <Sidebar
        activeThreadId={activeThreadId}
        onSelectThread={setActiveThreadId}
        onNewSession={handleNewSession}
      />
      <ChatWindow
        key={sessionKey}
        threadId={activeThreadId}
        onThreadCreated={setActiveThreadId}
      />
    </div>
  );
}
