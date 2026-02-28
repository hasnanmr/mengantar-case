# Frontend Documentation

This document provides an overview of the frontend implementation for the AI Sales Chatbot.

## Technology Stack

- **React**: Core UI framework.
- **CSS**: Custom vanilla styling for a premium look and feel.
- **Vite**: Build tool and development server.

## Features

- **Real-time Chat**: Interaction with the agent via WebSockets or streaming HTTP.
- **Stream Interrupts**: Users can hit the **Stop** button to abort active LLM generation dynamically.
- **Thread Management**: Users can start new conversations or continue existing ones.
- **Token Usage Badges**: Displays input, output, and total token count for each AI response (e.g., `🔢 in:X out:Y total:Z`).
- **Responsive Design**: Optimized for both desktop and mobile devices.
- **Markdown Rendering**: Support for rendering rich text and images (e.g., testimonials) using `react-markdown`.
- **Image Proxying**: Static assets (like testimonial photos) are proxied from the backend via Next.js `rewrites` configuration.

## UI Design

The interface features a **premium light theme** designed for clarity and a modern aesthetic:
- **Color Palette**: Brighter colors with a primary white/light-gray background and vibrant purple/pink gradients for accents.
- **Glassmorphism**: Subtle glass effects on cards and headers for a sophisticated look.
- **Typography**: Uses the Inter font family for high legibility.

## Structure

- `src/app/`: Contains the main layout and global styles (`globals.css`).
- `src/components/`: Reusable UI components (Sidebar, ChatWindow, etc.).
- `src/hooks/`: Custom React hooks for API interaction.
- `src/lib/`: API client and utility graduation.
