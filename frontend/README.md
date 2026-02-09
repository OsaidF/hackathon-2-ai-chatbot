# Todo AI Chatbot Frontend

A web-based chat interface for the Todo AI Chatbot, built with React, TypeScript, and Vite. Provides natural language task management through conversation.

## Features

- 🗣️ **Natural Language Interface**: Manage tasks through everyday language
- 💬 **Chat UI**: Clean, modern chat interface
- 🔄 **Conversation Persistence**: Conversations saved across sessions
- 📱 **Responsive Design**: Works seamlessly on mobile, tablet, and desktop
- ⚡ **Optimistic UI**: Instant feedback with rollback on errors
- 🔄 **Auto-Retry**: Automatic retry with exponential backoff on network failures
- 🌐 **Offline Detection**: Shows status indicator when offline
- ♿ **Accessible**: ARIA labels, keyboard navigation, and screen reader support

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000` (or configured URL)
- Valid backend authentication (development mode skips auth)

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# OpenAI ChatKit Domain Key (optional)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key

# Development Mode (enables placeholder auth)
VITE_DEV_MODE=true
```

### 3. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

The production bundle will be in `dist/`

## Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

### Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React UI components
│   ├── contexts/        # React Context providers
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API clients and business logic
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Helper functions
│   ├── styles/          # Global styles
│   ├── App.tsx          # Root component
│   └── main.tsx         # Entry point
├── .env                 # Environment variables (not in git)
├── .env.example         # Environment template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

### Key Components

- **ChatView** - Main chat container with responsive layout
- **MessageList** - Scrollable message display with auto-scroll
- **MessageItem** - Individual message with role-based styling
- **MessageInput** - Text input with validation and keyboard shortcuts
- **Header** - Top bar with logout and clear conversation
- **ErrorModal** - Error display with retry option
- **LoadingIndicator** - Loading spinner component

### State Management

- **AuthContext** - Authentication state (user, token)
- **ConversationContext** - Conversation and messages state
- **ChatKitContext** - ChatKit SDK wrapper

### API Integration

The frontend communicates with the backend via:

- **POST /api/v1/chat** - Send messages and get AI responses
- **GET /api/v1/health** - Health check endpoint

Request/Response format:

```typescript
// Request
{
  message: string;
  conversation_id?: string;
}

// Response
{
  conversation_id: string;
  user_message: string;
  assistant_message: string;
  history: Message[];
}
```

### Error Handling

- Network errors display in ErrorModal with retry option
- API errors show user-friendly messages
- Optimistic UI updates rollback on error
- Automatic retry with exponential backoff (1s, 2s, 4s)

## Deployment

### Vercel

1. Connect your GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard:
   - `VITE_API_BASE_URL` - Your production API URL
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` - Your ChatKit domain key (optional)
3. Deploy

### Netlify

1. Connect your GitHub repository to Netlify
2. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
3. Add environment variables in Netlify dashboard
4. Deploy

### Manual Deployment

1. Build the project:
   ```bash
   npm run build
   ```

2. Upload the `dist/` directory to your web server

3. Configure your web server to serve `index.html` for all routes (SPA)

### CORS Configuration

Ensure your backend allows requests from your frontend domain:

**backend/.env**:
```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

### ChatKit Domain Allowlist

Add your production domain to the ChatKit allowlist in your OpenAI dashboard.

## Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `VITE_API_BASE_URL` | Yes | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | No | ChatKit domain key | (empty) |
| `VITE_DEV_MODE` | No | Enable development mode | `true` |

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- **First Contentful Paint**: <1.5s (99th percentile)
- **Time to Interactive**: <3s (95th percentile)
- **Message Rendering**: <100ms (instant UI feedback)

## Troubleshooting

### Backend Connection Issues

If you see "Failed to fetch" errors:
1. Verify backend is running on the configured URL
2. Check CORS settings in backend
3. Verify `VITE_API_BASE_URL` in `.env`

### Authentication Errors

In development mode, authentication is automatically handled. If you see auth errors:
1. Ensure backend has `ENVIRONMENT=development` set
2. Check backend authentication logs

### Build Errors

If build fails:
1. Clear node_modules and reinstall: `rm -rf node_modules && npm install`
2. Ensure Node.js version is 18+
3. Check for TypeScript errors: `npm run build -- --mode development`

## License

MIT
