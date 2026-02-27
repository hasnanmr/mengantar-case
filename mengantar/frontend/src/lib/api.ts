const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchThreads() {
    const res = await fetch(`${API_BASE}/api/threads/`);
    if (!res.ok) throw new Error("Failed to fetch threads");
    return res.json();
}

export async function deleteThread(threadId: string) {
    const res = await fetch(`${API_BASE}/api/threads/${threadId}`, {
        method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete thread");
    return res.json();
}

export function streamChat(
    message: string,
    threadId: string | null,
    onToken: (token: string) => void,
    onUsage: (usage: { input_tokens: number; output_tokens: number; total_tokens: number }) => void,
    onDone: (data: { thread_id: string; stage: string }) => void,
    onError: (error: string) => void
) {
    const controller = new AbortController();

    fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, thread_id: threadId }),
        signal: controller.signal,
    }).then(async (res) => {
        if (!res.ok || !res.body) {
            onError("Failed to connect to chat service");
            return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (!line.startsWith("data: ")) continue;
                try {
                    const event = JSON.parse(line.slice(6));
                    if (event.type === "token") onToken(event.content);
                    else if (event.type === "usage") onUsage(event);
                    else if (event.type === "done") onDone(event);
                    else if (event.type === "error") onError(event.content);
                } catch { }
            }
        }
    }).catch((err) => {
        if (err.name !== "AbortError") onError(err.message);
    });

    return () => controller.abort();
}
