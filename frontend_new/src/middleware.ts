// frontend/src/middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  // Check if the current path is a protected route
  const pathname = request.nextUrl.pathname;
  const isProtectedRoute = 
    pathname.startsWith('/dashboard') || 
    pathname.startsWith('/todos') || 
    pathname.startsWith('/profile') || 
    pathname.startsWith('/tasks') || 
    pathname.startsWith('/chat');

  // Check if user has a valid token
  const token = request.cookies.get('token')?.value ||
                request.headers.get('authorization')?.replace('Bearer ', '');

  // If trying to access a protected route without a token, redirect to login
  if (isProtectedRoute && !token) {
    // Only redirect to login if not already on the login or signup page
    if (!pathname.startsWith('/login') && !pathname.startsWith('/signup')) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

// Specify which routes the middleware should run for
export const config = {
  matcher: [
    /*
     * Match only the routes that need authentication
     * This avoids potential issues with Vercel's internal functions
     */
    '/dashboard/:path*',
    '/todos/:path*',
    '/profile/:path*',
    '/tasks/:path*',
    '/chat/:path*',
  ],
}