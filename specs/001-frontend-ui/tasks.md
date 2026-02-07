# Tasks: Frontend UI & Integration

**Input**: Design documents from `/specs/001-frontend-ui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create frontend project structure per implementation plan in frontend/
- [x] T002 [P] Initialize Next.js project with App Router in frontend/package.json
- [x] T003 [P] Configure linting and formatting tools for JavaScript/TypeScript (ESLint, Prettier) in frontend/
- [x] T004 [P] Set up basic project configuration (tsconfig.json, next.config.js) in frontend/
- [x] T005 [P] Create initial directory structure (app/, components/, lib/, hooks/, styles/) in frontend/src/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Setup configuration management with BETTER_AUTH_SECRET in frontend/src/config/
- [x] T007 [P] Create API client utilities with JWT token handling in frontend/src/lib/api.ts
- [x] T008 [P] Create authentication service in frontend/src/lib/auth.ts
- [x] T009 [P] Create type definitions for User and Task entities in frontend/src/lib/types.ts
- [x] T010 [P] Set up basic layout and routing structure in frontend/src/app/layout.tsx
- [x] T011 Create authentication hooks (useAuth) in frontend/src/hooks/useAuth.ts
- [x] T012 Create task management hooks (useTasks) in frontend/src/hooks/useTasks.ts
- [x] T013 Configure environment variables for API endpoints in frontend/.env.local

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and securely log in to access their tasks

**Independent Test**: Register a new user account and successfully log in, delivering the ability to access a personalized task management experience.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Unit test for authentication service in frontend/tests/unit/auth.test.ts
- [ ] T015 [P] [US1] Integration test for login flow in frontend/tests/integration/login.test.ts

### Implementation for User Story 1

- [x] T016 [P] [US1] Create signup page component in frontend/src/app/signup/page.tsx
- [x] T017 [US1] Create login page component in frontend/src/app/login/page.tsx
- [x] T018 [US1] Implement signup form with validation in frontend/src/components/SignupForm.tsx
- [x] T019 [US1] Implement login form with validation in frontend/src/components/LoginForm.tsx
- [x] T020 [US1] Create private route component in frontend/src/components/PrivateRoute.tsx
- [x] T021 [US1] Implement authentication state management in frontend/src/lib/auth.ts
- [x] T022 [US1] Add redirect logic for unauthenticated users in frontend/src/components/PrivateRoute.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Management (Priority: P2)

**Goal**: Allow authenticated users to create, view, edit, delete, and mark tasks as completed from the UI

**Independent Test**: Create, view, edit, and delete tasks for an authenticated user, delivering the core task management functionality.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T023 [P] [US2] Unit test for task service in frontend/tests/unit/task.test.ts
- [ ] T024 [P] [US2] Integration test for task CRUD operations in frontend/tests/integration/task.test.ts

### Implementation for User Story 2

- [x] T025 [P] [US2] Create TaskList component in frontend/src/components/TaskList.tsx
- [x] T026 [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T027 [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [x] T028 [US2] Create dashboard page to display tasks in frontend/src/app/dashboard/page.tsx
- [x] T029 [US2] Create task detail page in frontend/src/app/tasks/[id]/page.tsx
- [x] T030 [US2] Implement task creation functionality in frontend/src/components/TaskForm.tsx
- [x] T031 [US2] Implement task editing functionality in frontend/src/components/TaskForm.tsx
- [x] T032 [US2] Implement task deletion functionality in frontend/src/components/TaskItem.tsx
- [x] T033 [US2] Implement task completion toggle in frontend/src/components/TaskItem.tsx
- [x] T034 [US2] Connect task components to API client in frontend/src/components/TaskList.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Secure Data Access and UI Responsiveness (Priority: P3)

**Goal**: Ensure authenticated users can only access their own tasks and cannot view or modify other users' tasks; UI works seamlessly across different screen sizes

**Independent Test**: Verify that users can only access their own tasks and not others', and that the UI works correctly on both mobile and desktop devices.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T035 [P] [US3] Unit test for user data isolation in frontend/tests/unit/isolation.test.ts
- [ ] T036 [P] [US3] Responsive design test in frontend/tests/e2e/responsive.test.ts

### Implementation for User Story 3

- [x] T037 [P] [US3] Implement user ID validation in API client to ensure user isolation in frontend/src/lib/api.ts
- [x] T038 [US3] Add responsive design classes to all components using Tailwind CSS
- [x] T039 [US3] Create loading and error state components in frontend/src/components/LoadingSpinner.tsx
- [x] T040 [US3] Implement proper error handling and display in UI components
- [x] T041 [US3] Add token expiration handling in frontend/src/lib/auth.ts
- [x] T042 [US3] Create mobile-first responsive layouts for all pages
- [x] T043 [US3] Implement proper accessibility attributes in all components

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T044 [P] Documentation updates in docs/
- [x] T045 Code cleanup and refactoring
- [x] T046 Performance optimization across all stories
- [ ] T047 [P] Additional unit tests (if requested) in frontend/tests/unit/
- [x] T048 Security hardening
- [x] T049 [P] Responsive design improvements in frontend/src/styles/
- [x] T050 [P] Error boundary implementation in frontend/src/components/
- [x] T051 Run quickstart.md validation
- [x] T052 Update environment configuration with database URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for authentication service in frontend/tests/unit/auth.test.ts"
Task: "Integration test for login flow in frontend/tests/integration/login.test.ts"

# Launch all components for User Story 1 together:
Task: "Create signup page component in frontend/src/app/signup/page.tsx"
Task: "Create login page component in frontend/src/app/login/page.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence