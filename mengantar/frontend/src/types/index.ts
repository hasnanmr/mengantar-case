export interface Thread {
  thread_id: string;
  last_checkpoint?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  tokenUsage?: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
}

export type ConversationStage =
  | "greeting"
  | "needs_assessment"
  | "consultation"
  | "social_proof"
  | "promotion"
  | "closing"
  | "end";
