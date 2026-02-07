---
name: backend-error-skill
description: Diagnose, troubleshoot, and resolve backend runtime errors, package issues, environment misconfigurations, and server deployment problems.
---

# Backend Error Handling Skill

## Purpose
This skill is designed to help developers quickly identify, debug, and fix backend errors in a structured, step-by-step manner. It covers:

- Runtime errors (Python, Node.js, PHP, etc.)
- Package and dependency issues
- Environment and configuration problems
- Database connectivity and API errors
- Deployment and server startup errors

## Instructions

1. **Error Collection**
   - Always request the full error message and stack trace.
   - Identify the language/runtime (Python, Node.js, etc.).
   - Ask for relevant project files like `package.json`, `requirements.txt`, `.env`, or config files.

2. **Error Classification**
   - Syntax Errors: Missing symbols, typos, incorrect code structure.
   - Runtime Errors: Exceptions, null references, invalid operations.
   - Dependency Errors: Missing or incompatible packages/modules.
   - Environment Errors: Wrong runtime versions, misconfigured environment variables.
   - Server/Deployment Errors: Port conflicts, missing build files, incorrect permissions.
   - Database/API Errors: Connection failures, invalid credentials, or schema mismatches.

3. **Diagnosis Steps**
   - **Check environment**: Runtime version (`node -v` / `python --version`) and OS compatibility.
   - **Check dependencies**: Ensure all packages are installed and compatible.
   - **Verify configuration**: Validate `.env` variables, database URLs, API keys.
   - **Check logs**: Look for repeated warnings or errors before the crash.
   - **Simplify reproduction**: Isolate the issue in a minimal example if possible.

4. **Fix Recommendations**
   - Provide exact terminal commands to install or fix missing packages:
     ```bash
     npm install <package>@latest
     pip install <package> --upgrade
     ```
   - Suggest code corrections for syntax or runtime issues.
   - Advise on environment fixes:
     - Correct Python/Node.js version
     - Update `.env` or config files
     - Rebuild or restart services
   - Include optional preventive measures to avoid recurring errors.

5. **Follow-Up**
   - Ask the user to retry after applying fixes.
   - If the issue persists, request additional context: folder structure, relevant code snippets, or error logs.
   - Provide best practices to prevent similar errors in the future.

## Best Practices
- Always validate the runtime and environment first.
- Avoid destructive commands unless necessary, and warn the user explicitly.
- Provide clear, step-by-step fixes, not just general advice.
- Encourage modular and clean backend code to reduce future errors.
- Include preventive steps: logging, version checks, and dependency management.

