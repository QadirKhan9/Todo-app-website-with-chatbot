---
name: frontend-debug
description: Diagnose and fix npm installation issues, Next.js build errors, and runtime frontend errors.
---

# Frontend Debug Skill

## Purpose
Automatically analyze, classify, and suggest fixes for frontend errors in a Next.js project, including:

- npm / yarn / pnpm installation errors
- Dependency version conflicts
- Build-time Next.js errors
- Runtime errors (React hydration, API client failures)
- Better Auth frontend integration issues

## Instructions

1. **Error Identification**
   - Detect exact error type: install error, build error, runtime error, or config issue.
   - Capture full error message and affected file/package.

2. **Root Cause Analysis**
   - Determine the underlying cause:
     - Version mismatch
     - Missing dependency
     - Misconfigured environment variable
     - Frontend-backend integration issue

3. **Fix Recommendation**
   - Provide precise commands or config changes.
   - Minimize changes; avoid unnecessary deletions or rewrites.
   - Include OS-aware instructions if relevant (Linux / Windows / macOS).

4. **Verification**
   - Provide steps to confirm the error is resolved.
   - Suggest testing key flows like:
     - npm install or build
     - Page rendering and API fetch
     - Authentication flows

5. **Prevention Tip (Optional)**
   - Suggest best practices to avoid recurring errors, e.g., lockfile usage, Node.js version management, environment variable validation.

## Constraints
- Do not modify backend code.
- Do not rewrite application logic.
- Do not introduce new libraries unless required for fix.
- Focus only on frontend errors.
- Compatible with Next.js 16+ App Router and Better Auth integration.

## Success Criteria
- npm install completes without errors.
- Next.js app builds successfully.
- Runtime errors eliminated.
- Auth integration works correctly.
- Fix is minimal, reproducible, and safe.
