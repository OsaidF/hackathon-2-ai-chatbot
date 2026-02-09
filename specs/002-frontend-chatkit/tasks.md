# Tasks: Todo AI Chatbot Frontend with OpenAI ChatKit

**Input**: Design documents from `/specs/002-frontend-chatkit/`
**Prerequisites**: spec.md (user stories), implementation plan (C:\Users\Ebad\.claude\plans\jaunty-cooking-kurzweil.md)

**Tests**: Component and integration tests can be added during implementation. Tests are OPTIONAL per spec unless user requests TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web application**: `frontend/src/` for source files
- Frontend is a separate single-page application connecting to existing backend at localhost:8000

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Vite + React + TypeScript project in frontend/ directory
- [x] T002 [P] Install dependencies: openai/chatkit-js, react-dom, axios in frontend/package.json
- [x] T003 [P] Install dev dependencies: @types/react, @types/react-dom, @vitejs/plugin-react, typescript, vite
- [x] T004 [P] Create frontend/.env.example with VITE_API_BASE_URL and NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- [x] T005 [P] Create frontend/.env from .env.example with local development values
- [x] T006 [P] Create frontend/vite.config.ts with React plugin and proxy to localhost:8000
- [x] T007 [P] Create frontend/tsconfig.json with TypeScript configuration for React
- [x] T008 [P] Create frontend/index.html with proper meta tags and viewport configuration
- [x] T009 [P] Create frontend/src/styles/variables.css with CSS design tokens (colors, spacing, breakpoints)
- [x] T010 [P] Create frontend/src/styles/global.css with global styles and reset
- [x] T011 Create frontend/src/types/chat.ts with Message and Conversation TypeScript interfaces
- [x] T012 Create frontend/src/types/api.ts with ChatRequest and ChatResponse TypeScript interfaces
- [x] T013 Create frontend/src/types/errors.ts with ApiError TypeScript interface
- [x] T014 Create frontend/src/utils/constants.ts with API URLs, message length limits, and configuration constants
- [x] T015 Create frontend/src/utils/validation.ts with message validation functions (empty check, max length)
- [x] T016 Create frontend/src/utils/formatting.ts with task formatting and text processing utilities
- [x] T017 Create frontend/src/main.tsx as React application entry point
- [x] T018 Create frontend/src/App.tsx as root component
- [x] T019 Create frontend/src/App.module.css with App component styles

**Checkpoint**: ✅ Project structure ready with all configuration files and type definitions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Context Providers

- [x] T020 Create frontend/src/contexts/AuthContext.tsx with authentication state provider
- [x] T021 [P] Create frontend/src/contexts/ConversationContext.tsx with conversation and message state provider
- [x] T022 [P] Create frontend/src/contexts/ChatKitContext.tsx as ChatKit SDK wrapper

### Service Layer

- [x] T023 Create frontend/src/services/storage.ts with localStorage helper functions (save/load conversation ID)
- [x] T024 Create frontend/src/services/authManager.ts with JWT token management (getToken, setToken, clearToken)
- [x] T025 Create frontend/src/services/apiClient.ts with HTTP client, retry logic (exponential backoff, 3 attempts), and error handling

### Hooks

- [x] T026 [P] Create frontend/src/hooks/useAuth.ts as auth state wrapper hook
- [x] T027 [P] Create frontend/src/hooks/useConversation.ts as conversation state wrapper hook
- [x] T028 [P] Create frontend/src/hooks/useChatKit.ts as ChatKit integration hook

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage their personal todo list through conversational chat interface using everyday language

**Independent Test**: User can open chat interface, send natural language messages to manage tasks (create, list, complete, delete, update), and see results without using forms or command syntax. Tasks persist across page refreshes.

### Core Chat Components

- [x] T029 [P] [US1] Create frontend/src/components/ChatView.tsx as main chat container component with responsive layout
- [x] T030 [P] [US1] Create frontend/src/components/ChatView.module.css with ChatView responsive styles
- [x] T031 [P] [US1] Create frontend/src/components/MessageList.tsx as scrollable message display component
- [x] T032 [P] [US1] Create frontend/src/components/MessageList.module.css with MessageList styles and scroll behavior
- [x] T033 [P] [US1] Create frontend/src/components/MessageItem.tsx as individual message component with role-based styling (user vs assistant)
- [x] T034 [P] [US1] Create frontend/src/components/MessageItem.module.css with MessageItem styles for different message roles
- [x] T035 [P] [US1] Create frontend/src/components/MessageInput.tsx as text input component with validation (empty check, 10k char limit)
- [x] T036 [P] [US1] Create frontend/src/components/MessageInput.module.css with MessageInput styles and validation feedback

### Chat Functionality

- [x] T037 [US1] Implement auto-scroll to latest message in MessageList component
- [x] T038 [US1] Implement keyboard shortcuts in MessageInput (Enter to send, Shift+Enter for newline)
- [x] T039 [US1] Wire up MessageInput send button to apiClient.sendMessage in frontend/src/components/MessageInput.tsx
- [x] T040 [US1] Implement optimistic UI updates (show user message immediately, rollback on error) in ConversationContext
- [x] T041 [US1] Display loading indicator during API response wait in frontend/src/components/MessageList.tsx
- [x] T042 [US1] Format task mentions in messages (checkboxes, status indicators) in frontend/src/components/MessageItem.tsx
- [x] T043 [US1] Support emoji and special characters in task titles in frontend/src/components/MessageItem.tsx

### API Integration

- [x] T044 [US1] Wire up ChatKit hook to backend POST /api/v1/chat endpoint in frontend/src/hooks/useChatKit.ts
- [x] T045 [US1] Implement conversation ID lifecycle (generate on first message, save to localStorage, load on mount) in ConversationContext
- [x] T046 [US1] Handle API errors with user-friendly messages in frontend/src/components/ErrorModal.tsx
- [x] T047 [US1] Implement message validation (prevent empty messages) in frontend/src/components/MessageInput.tsx

**Checkpoint**: ✅ At this point, User Story 1 should be fully functional - users can manage tasks through natural language conversation

---

## Phase 4: User Story 2 - Seamless Conversation Continuity (Priority: P2)

**Goal**: Users can leave the chat interface and return later without losing context, seeing full conversation history

**Independent Test**: User creates tasks, closes browser tab, reopens it, and sees complete conversation history intact with all task context preserved

### Header Component

- [x] T048 [P] [US2] Create frontend/src/components/Header.tsx as top bar component with logo and user controls
- [x] T049 [P] [US2] Create frontend/src/components/Header.module.css with Header styles

### Persistence Features

- [x] T050 [US2] Implement load conversation on app mount in ConversationContext (read conversation ID from localStorage)
- [x] T051 [US2] Implement save conversation ID after first message in ConversationContext (write to localStorage)
- [x] T052 [US2] Add clear conversation button to Header component with confirmation dialog
- [x] T053 [US2] Implement clear conversation functionality in ConversationContext (clear localStorage, reset state)
- [x] T054 [US2] Add logout button to Header component
- [x] T055 [US2] Implement logout functionality in AuthContext (clear token, clear conversation state)

### Error Handling

- [x] T056 [P] [US2] Create frontend/src/components/ErrorModal.tsx as error display component
- [x] T057 [P] [US2] Create frontend/src/components/ErrorModal.module.css with ErrorModal styles
- [x] T058 [US2] Add retry button to ErrorModal component for failed requests
- [x] T059 [US2] Implement network status detection (online/offline) in frontend/src/services/apiClient.ts
- [x] T060 [US2] Display network connectivity indicator in ChatView component

**Checkpoint**: ✅ At this point, User Stories 1 AND 2 should both work independently with full conversation persistence

---

## Phase 5: User Story 3 - Responsive Access on Any Device (Priority: P3)

**Goal**: Interface works seamlessly on desktop, tablet, and mobile with consistent experience

**Independent Test**: User opens chat on desktop, mobile phone, and tablet; all task management operations work with interface adapting to screen size

### Loading Indicator

- [x] T061 [P] [US3] Create frontend/src/components/LoadingIndicator.tsx as loading spinner/skeleton component
- [x] T062 [P] [US3] Create frontend/src/components/LoadingIndicator.module.css with LoadingIndicator styles

### Mobile Styles (< 768px)

- [x] T063 [US3] Implement mobile full-screen layout in frontend/src/components/ChatView.module.css
- [x] T064 [US3] Add touch-friendly target sizes in frontend/src/components/MessageInput.module.css
- [x] T065 [US3] Adjust for virtual keyboard (viewport changes) in frontend/src/components/ChatView.module.css
- [x] T066 [US3] Optimize font sizes for mobile screens in frontend/src/styles/variables.css

### Tablet Styles (768px - 1023px)

- [x] T067 [US3] Implement centered chat container (max-width 700px) in frontend/src/components/ChatView.module.css
- [x] T068 [US3] Add enhanced spacing for tablet in frontend/src/components/MessageList.module.css

### Desktop Styles (1024px+)

- [x] T069 [US3] Implement centered chat container (max-width 900px) in frontend/src/components/ChatView.module.css
- [x] T070 [US3] Add hover states for buttons in frontend/src/components/MessageInput.module.css
- [x] T071 [US3] Implement enhanced typography for desktop in frontend/src/styles/variables.css

### Orientation Handling

- [x] T072 [US3] Handle orientation changes (portrait ↔ landscape) in frontend/src/components/ChatView.tsx
- [x] T073 [US3] Test and fix layout issues on orientation changes in frontend/src/components/ChatView.module.css

**Checkpoint**: ✅ All user stories should now be independently functional with full responsive design

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [x] T074 [P] Create frontend/README.md with setup instructions, environment variables, and development guide
- [x] T075 [P] Update root README.md with frontend development instructions

### Final Polish

- [x] T076 [P] Add character counter to MessageInput component in frontend/src/components/MessageInput.tsx
- [x] T077 [P] Improve accessibility (ARIA labels, keyboard navigation) in frontend/src/components/ChatView.tsx
- [x] T078 [P] Add placeholder text to MessageInput component in frontend/src/components/MessageInput.tsx
- [ ] T079 [P] Optimize message rendering performance (virtualization if >100 messages) in frontend/src/components/MessageList.tsx (optional - can be added later if needed)
- [x] T080 [P] Add favicon.svg to frontend/public/
- [x] T081 [P] Configure production build optimizations in frontend/vite.config.ts
- [x] T082 [P] Add error boundary for React component errors in frontend/src/App.tsx

### Deployment Preparation

- [x] T083 [P] Test production build (npm run build) in frontend/ directory
- [x] T084 [P] Create deployment documentation in frontend/README.md
- [x] T085 [P] Document CORS configuration for production deployment in frontend/README.md
- [x] T086 Document ChatKit domain allowlist configuration in frontend/README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 with persistence features
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Adds responsive design to existing UI

### Within Each User Story

- Components marked [P] can be created in parallel (different files)
- Chat functionality tasks depend on core components being created
- API integration depends on service layer completion
- US2 persistence features depend on US1 chat components
- US3 styles build upon US1/US2 component structure

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T010)
- All Foundational context provider tasks marked [P] can run in parallel (T021-T022)
- All Foundational hook tasks marked [P] can run in parallel (T026-T028)
- US1 core components (T029-T036) can all be created in parallel
- US2 Header component (T048-T049) can be created in parallel with other US2 features
- US3 LoadingIndicator (T061-T062) can be created in parallel with style tasks
- All Polish tasks marked [P] can run in parallel (T074-T086)

---

## Parallel Example: User Story 1

```bash
# Launch all core component files together (T029-T036):
Task: "Create frontend/src/components/ChatView.tsx"
Task: "Create frontend/src/components/MessageList.tsx"
Task: "Create frontend/src/components/MessageItem.tsx"
Task: "Create frontend/src/components/MessageInput.tsx"

# Then implement functionality (sequential):
Task: "Implement auto-scroll in MessageList" (T037)
Task: "Implement keyboard shortcuts in MessageInput" (T038)
Task: "Wire up MessageInput to apiClient" (T039)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**MVP Deliverables**:
- Users can manage tasks through natural language conversation
- Chat interface displays messages chronologically
- Basic loading states and error handling
- Conversation ID persistence (localStorage)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Complete Polish → Production release

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (chat components and functionality)
   - Developer B: User Story 2 (persistence and header features)
   - Developer C: User Story 3 (responsive design and loading states)
3. Stories complete and integrate independently
4. Team completes Polish phase together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Frontend is stateless client**: All conversation state persisted to backend via API
- **localStorage used sparingly**: Only for conversation ID and JWT token (constitutional principle III)
- **ChatKit integration**: Hosted ChatKit connected to custom FastAPI backend
- **Responsive first**: Mobile-first CSS approach, enhanced for tablet/desktop
