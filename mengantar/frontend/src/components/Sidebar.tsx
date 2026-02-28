"use client";
import { useEffect, useState } from "react";
import { Thread } from "@/types";
import { fetchThreads, deleteThread } from "@/lib/api";

interface SidebarProps {
    activeThreadId: string | null;
    onSelectThread: (threadId: string) => void;
    onNewSession: () => void;
    isCollapsed: boolean;
}

export default function Sidebar({ activeThreadId, onSelectThread, onNewSession, isCollapsed }: SidebarProps) {
    const [threads, setThreads] = useState<Thread[]>([]);

    const loadThreads = async () => {
        try {
            const data = await fetchThreads();
            setThreads(data.threads || []);
        } catch (err) {
            console.error("Failed to load threads:", err);
        }
    };

    useEffect(() => {
        loadThreads();
        const interval = setInterval(loadThreads, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleDelete = async (e: React.MouseEvent, threadId: string) => {
        e.stopPropagation();
        await deleteThread(threadId);
        setThreads((prev) => prev.filter((t) => t.thread_id !== threadId));
        if (activeThreadId === threadId) onNewSession();
    };

    const shortId = (id: string) => `Session ${id.slice(0, 8)}...`;

    return (
        <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
            <div className="sidebar-logo">
                <div className="logo-icon">✨</div>
                <div>
                    <h2>Acne Care</h2>
                    <span>AI Sales Assistant</span>
                </div>
            </div>

            <button className="new-session-btn" onClick={onNewSession}>
                <span>+</span> New Session
            </button>

            <div className="thread-list">
                <p className="thread-list-title">Recent Sessions</p>
                {threads.length === 0 && (
                    <p style={{ fontSize: 12, color: "var(--text-muted)", padding: "4px" }}>
                        No sessions yet
                    </p>
                )}
                {threads.map((thread) => (
                    <div
                        key={thread.thread_id}
                        className={`thread-item ${activeThreadId === thread.thread_id ? "active" : ""}`}
                        onClick={() => onSelectThread(thread.thread_id)}
                    >
                        <span className="thread-item-icon">💬</span>
                        <div className="thread-item-text">
                            <p className="thread-item-id">{shortId(thread.thread_id)}</p>
                            <p className="thread-item-time">Click to continue</p>
                        </div>
                        <button
                            className="thread-delete-btn"
                            onClick={(e) => handleDelete(e, thread.thread_id)}
                            title="Delete session"
                        >
                            ✕
                        </button>
                    </div>
                ))}
            </div>
        </aside>
    );
}
