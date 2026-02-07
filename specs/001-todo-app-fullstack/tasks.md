---

description: "Task list template for feature implementation"
---

# Tasks: Todo Full-Stack Web Application

**Input**: Design documents from `/specs/001-todo-app-fullstack/`
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

<!--
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.

  The /sp.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/

  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment

  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend project structure per implementation plan in backend/
- [x] T002 Create frontend project structure per implementation plan in frontend/
- [x] T003 [P] Initialize Python project with FastAPI, SQLModel dependencies in backend/requirements.txt
- [x] T004 [P] Initialize Next.js project with App Router in frontend/package.json
- [x] T005 [P] Configure linting and formatting tools for Python (black, flake8) in backend/
- [x] T006 [P] Configure linting and formatting tools for JavaScript/TypeScript (ESLint, Prettier) in frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T007 Setup database schema and migrations framework with Alembic in backend/
- [x] T008 [P] Implement JWT authentication framework in backend/src/auth/
- [x] T009 [P] Setup Better Auth integration in frontend/src/lib/auth.ts
- [x] T010 [P] Setup API routing and middleware structure in backend/src/api/
- [x] T011 Create base models/entities that all stories depend on in backend/src/models/
- [x] T012 Configure error handling and logging infrastructure in backend/src/utils/
- [x] T013 Setup environment configuration management in backend/src/config/
- [x] T014 Create API client utilities in frontend/src/lib/api.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to create accounts and securely log in to access their tasks

**Independent Test**: Register a new user account and successfully log in, delivering the ability to access a personalized task management experience.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T015 [P] [US1] Contract test for auth endpoints in backend/tests/contract/test_auth.py
- [ ] T016 [P] [US1] Integration test for user registration flow in backend/tests/integration/test_user_registration.py

### Implementation for User Story 1

- [x] T017 [P] [US1] Create User model in backend/src/models/user.py
- [x] T018 [US1] Implement authentication service in backend/src/services/auth_service.py
- [x] T019 [US1] Implement auth endpoints (register, login, logout) in backend/src/api/auth.py
- [x] T020 [US1] Create login page component in frontend/src/app/login/page.tsx
- [x] T021 [US1] Create register page component in frontend/src/app/register/page.tsx
- [x] T022 [US1] Implement session management in frontend/src/lib/auth.ts
- [x] T023 [US1] Add authentication middleware to protect routes in frontend/src/middleware.ts

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Management (Priority: P2)

**Goal**: Allow authenticated users to create, view, edit, and delete their tasks, and mark tasks as completed

**Independent Test**: Create, view, edit, and delete tasks for an authenticated user, delivering the core task management functionality.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US2] Contract test for task endpoints in backend/tests/contract/test_tasks.py
- [ ] T025 [P] [US2] Integration test for task management flow in backend/tests/integration/test_task_management.py

### Implementation for User Story 2

- [x] T026 [P] [US2] Create Task model in backend/src/models/task.py
- [x] T027 [US2] Implement task service in backend/src/services/task_service.py
- [x] T028 [US2] Implement task endpoints (CRUD operations) in backend/src/api/tasks.py
- [x] T029 [US2] Create TaskItem component in frontend/src/components/TaskItem.tsx
- [x] T030 [US2] Create TaskForm component in frontend/src/components/TaskForm.tsx
- [x] T031 [US2] Create TaskList component in frontend/src/components/TaskList.tsx
- [x] T032 [US2] Create dashboard page to display tasks in frontend/src/app/dashboard/page.tsx
- [x] T033 [US2] Connect frontend components to backend API in frontend/src/lib/api.ts

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Secure Data Access (Priority: P3)

**Goal**: Ensure authenticated users can only access their own tasks and cannot view or modify other users' tasks

**Independent Test**: Verify that users can only access their own tasks and not others', delivering secure data isolation.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T034 [P] [US3] Contract test for user access control in backend/tests/contract/test_access_control.py
- [ ] T035 [P] [US3] Integration test for user data isolation in backend/tests/integration/test_data_isolation.py

### Implementation for User Story 3

- [x] T036 [P] [US3] Implement user ID extraction from JWT in backend/src/auth/
- [x] T037 [US3] Add user ID validation to task endpoints in backend/src/api/tasks.py
- [x] T038 [US3] Implement database-level filtering by user ID in backend/src/services/task_service.py
- [x] T039 [US3] Add frontend validation to ensure user only sees their tasks in frontend/src/lib/api.ts
- [x] T040 [US3] Implement error handling for unauthorized access attempts in backend/src/api/tasks.py

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T041 [P] Documentation updates in docs/
- [ ] T042 Code cleanup and refactoring
- [ ] T043 Performance optimization across all stories
- [ ] T044 [P] Additional unit tests (if requested) in backend/tests/unit/ and frontend/tests/unit/
- [ ] T045 Security hardening
- [ ] T046 [P] Responsive design improvements in frontend/src/styles/
- [ ] T047 [P] Error boundary implementation in frontend/src/components/
- [ ] T048 Run quickstart.md validation

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
Task: "Contract test for auth endpoints in backend/tests/contract/test_auth.py"
Task: "Integration test for user registration flow in backend/tests/integration/test_user_registration.py"

# Launch all models for User Story 1 together:
Task: "Create User model in backend/src/models/user.py"
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