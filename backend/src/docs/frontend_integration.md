"""
TOKEN LIFECYCLE & FRONTEND INTEGRATION
====================================

TOKEN TYPES
-----------

1. Access Token:
   - Short-lived (30 minutes by default)
   - Used for authenticating API requests
   - Stored in memory (not localStorage for security)
   - Sent in Authorization header: "Bearer {token}"

2. Refresh Token:
   - Long-lived (7 days by default)
   - Used to obtain new access tokens
   - Stored securely (preferably in httpOnly cookie)
   - Used only for /refresh endpoint


TOKEN LIFECYCLE
---------------

1. User logs in → receives both access and refresh tokens
2. Access token used for protected API calls
3. When access token expires:
   - Frontend calls /refresh endpoint with refresh token
   - Gets new access token (and possibly new refresh token)
4. If refresh token expires → user must log in again


FRONTEND INTEGRATION
--------------------

1. Storage Strategy:
   - Access token: Store in memory/state (not localStorage)
   - Refresh token: Store in httpOnly cookie if possible, otherwise in localStorage with extra security measures

2. API Request Interceptor:
   - Add Authorization header to all requests
   - Handle 401 responses by attempting token refresh
   - Redirect to login if refresh fails

3. Example Implementation:
   ```javascript
   // Store tokens
   const storeTokens = (tokens) => {
     sessionStorage.setItem('accessToken', tokens.access_token);
     // Refresh token should ideally be stored in httpOnly cookie
   };

   // Get access token
   const getAccessToken = () => {
     return sessionStorage.getItem('accessToken');
   };

   // API request with automatic refresh
   const apiCall = async (url, options = {}) => {
     const accessToken = getAccessToken();
     
     const headers = {
       ...options.headers,
       'Authorization': `Bearer ${accessToken}`,
       'Content-Type': 'application/json'
     };

     let response = await fetch(url, { ...options, headers });

     // If 401 and access token expired, try to refresh
     if (response.status === 401) {
       const refreshResult = await refreshToken();
       if (refreshResult.success) {
         // Retry original request with new token
         const newAccessToken = sessionStorage.getItem('accessToken');
         headers['Authorization'] = `Bearer ${newAccessToken}`;
         response = await fetch(url, { ...options, headers });
       } else {
         // Redirect to login
         window.location.href = '/login';
       }
     }

     return response;
   };
   ```

4. Protected Routes:
   - Check for valid access token before allowing access
   - Implement automatic token refresh in background
   - Handle logout by clearing tokens and redirecting


SECURITY CONSIDERATIONS
---------------------

1. Never store access tokens in localStorage (XSS risk)
2. Use httpOnly cookies for refresh tokens when possible
3. Implement CSRF protection
4. Use HTTPS in production
5. Set appropriate token expiration times
6. Rotate refresh tokens periodically
7. Implement rate limiting for auth endpoints
"""