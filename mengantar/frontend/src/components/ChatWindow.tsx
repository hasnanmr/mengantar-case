"use client";
import { useEffect, useRef, useState } from "react";
import { Message, ConversationStage } from "@/types";
import { streamChat } from "@/lib/api";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import ErrorBoundary from "@/components/ErrorBoundary";
import ReactMarkdown from "react-markdown";

interface ChatWindowProps {
    threadId: string | null;
    onThreadCreated: (id: string) => void;
    isSidebarCollapsed: boolean;
    onToggleSidebar: () => void;
}

const QUICK_STARTS = [
    "Halo, saya punya masalah jerawat 🙋",
    "Produk apa yang cocok untuk kulit berminyak?",
    "Ada rekomendasi skincare untuk jerawat?",
];

export default function ChatWindow({ threadId, onThreadCreated, isSidebarCollapsed, onToggleSidebar }: ChatWindowProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState(false);
    const [streamingMsg, setStreamingMsg] = useState("");
    const [stage, setStage] = useState<ConversationStage>("greeting");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const abortRef = useRef<(() => void) | null>(null);

    // Load history when threadId changes
    useEffect(() => {
        if (!threadId) {
            setMessages([]);
            setStage("greeting");
            return;
        }

        const loadHistory = async () => {
            setIsLoadingHistory(true);
            setMessages([]); // Clear stale messages
            try {
                const { fetchThreadHistory } = await import("@/lib/api");
                const data = await fetchThreadHistory(threadId);
                const history = data.messages.map((m: any) => ({
                    ...m,
                    timestamp: m.timestamp ? new Date(m.timestamp) : new Date(),
                }));
                setMessages(history);
                setStage(data.stage as ConversationStage);
            } catch (err) {
                console.error("Failed to load history:", err);
                setMessages([]); // Ensure it's clear on error
            } finally {
                setIsLoadingHistory(false);
            }
        };

        loadHistory();
    }, [threadId]);

    // Auto-scroll
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, streamingMsg]);

    const sendMessage = (text: string) => {
        if (!text.trim() || isStreaming) return;
        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: text.trim(),
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsStreaming(true);
        setStreamingMsg("");

        let accumulated = "";
        let usageData: Message["tokenUsage"];

        const abort = streamChat(
            text.trim(),
            threadId,
            (token) => { accumulated += token; setStreamingMsg(accumulated); },
            (usage) => { usageData = usage; },
            (done) => {
                onThreadCreated(done.thread_id);
                setStage(done.stage as ConversationStage);
                const aiMsg: Message = {
                    id: Date.now().toString() + "-ai",
                    role: "assistant",
                    content: accumulated,
                    timestamp: new Date(),
                    tokenUsage: usageData,
                };
                setMessages((prev) => [...prev, aiMsg]);
                setStreamingMsg("");
                setIsStreaming(false);
            },
            (err) => {
                const errMsg: Message = {
                    id: Date.now().toString() + "-err",
                    role: "assistant",
                    content: `⚠️ Error: ${err}`,
                    timestamp: new Date(),
                };
                setMessages((prev) => [...prev, errMsg]);
                setIsStreaming(false);
                setStreamingMsg("");
            }
        );
        abortRef.current = abort;
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage(input);
        }
    };

    const hasMessages = messages.length > 0;

    return (
        <ErrorBoundary>
            <div className="chat-area">
                {/* Header */}
                <div className="chat-header">
                    <button
                        className="sidebar-toggle-btn"
                        onClick={onToggleSidebar}
                        aria-label={isSidebarCollapsed ? "Show sidebar" : "Hide sidebar"}
                        title={isSidebarCollapsed ? "Show sidebar" : "Hide sidebar"}
                    >
                        {isSidebarCollapsed ? "☰" : "✕"}
                    </button>
                    <div className="chat-header-avatar">🤖</div>
                    <div className="chat-header-info">
                        <h3>Acne Care Assistant</h3>
                        <span>● Online</span>
                    </div>
                    {hasMessages && (
                        <span className="chat-stage-badge">{stage.replace("_", " ")}</span>
                    )}
                </div>

                {/* Messages */}
                <div className="messages-container">
                    {isLoadingHistory ? (
                        <div style={{ padding: "20px" }}>
                            <LoadingSkeleton />
                        </div>
                    ) : !hasMessages ? (
                        <div className="welcome-screen">
                            <div className="welcome-logo">✨</div>
                            <h1>Acne Care Assistant</h1>
                            <p>
                                Konsultasi gratis seputar perawatan kulit jerawat. Tim kami siap membantu kamu menemukan solusi terbaik!
                            </p>
                            <div className="quick-starts">
                                {QUICK_STARTS.map((q) => (
                                    <button key={q} className="quick-start-btn" onClick={() => sendMessage(q)}>
                                        {q}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <>
                            {messages.map((msg) => (
                                <div key={msg.id} className={`message-row ${msg.role}`}>
                                    <div className="message-avatar">
                                        {msg.role === "assistant" ? "🤖" : "😊"}
                                    </div>
                                    <div>
                                        <div className="message-bubble">
                                            {msg.role === "assistant" ? (
                                                <ReactMarkdown
                                                    components={{
                                                        img: ({ src, alt }) => {
                                                            const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                                                            const resolvedSrc = typeof src === "string" && src.startsWith("/static") ? `${apiBase}${src}` : src;
                                                            return (
                                                                <img
                                                                    src={resolvedSrc}
                                                                    alt={alt}
                                                                    style={{
                                                                        maxWidth: "100%",
                                                                        borderRadius: "12px",
                                                                        marginTop: "8px",
                                                                        display: "block",
                                                                    }}
                                                                />
                                                            )
                                                        },
                                                    }}
                                                >
                                                    {msg.content}
                                                </ReactMarkdown>
                                            ) : (
                                                msg.content
                                            )}
                                        </div>
                                        {msg.tokenUsage && (
                                            <div className="token-badge">
                                                🔢 in:{msg.tokenUsage.input_tokens} out:{msg.tokenUsage.output_tokens} total:{msg.tokenUsage.total_tokens}
                                            </div>
                                        )}
                                        <p className="message-meta">
                                            {msg.timestamp.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })}
                                        </p>
                                    </div>
                                </div>
                            ))}

                            {/* Streaming or typing */}
                            {isStreaming && (
                                <div className="message-row assistant">
                                    <div className="message-avatar">🤖</div>
                                    {streamingMsg ? (
                                        <div className="message-bubble">
                                            <ReactMarkdown
                                                components={{
                                                    img: ({ src, alt }) => {
                                                        const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
                                                        const resolvedSrc = typeof src === "string" && src.startsWith("/static") ? `${apiBase}${src}` : src;
                                                        return (
                                                            <img
                                                                src={resolvedSrc}
                                                                alt={alt}
                                                                style={{
                                                                    maxWidth: "100%",
                                                                    borderRadius: "12px",
                                                                    marginTop: "8px",
                                                                    display: "block",
                                                                }}
                                                            />
                                                        )
                                                    },
                                                }}
                                            >
                                                {streamingMsg}
                                            </ReactMarkdown>
                                        </div>
                                    ) : (
                                        <LoadingSkeleton />
                                    )}
                                </div>
                            )}
                        </>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="input-area">
                    <div className="input-container">
                        <textarea
                            className="chat-input"
                            placeholder="Ketik pesanmu di sini..."
                            rows={1}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={isStreaming}
                        />
                        {isStreaming && (
                            <button
                                className="stop-btn"
                                onClick={() => {
                                    if (abortRef.current) {
                                        abortRef.current();
                                        abortRef.current = null;
                                        setIsStreaming(false);
                                        setStreamingMsg("");
                                    }
                                }}
                                aria-label="Stop streaming"
                            >
                                ⏹
                            </button>
                        )}
                        <button
                            className="send-btn"
                            onClick={() => sendMessage(input)}
                            disabled={!input.trim() || isStreaming}
                            aria-label="Send message"
                        >
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        </ErrorBoundary>
    );
}
