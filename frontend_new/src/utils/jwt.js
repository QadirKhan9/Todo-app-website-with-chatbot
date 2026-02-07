// frontend/src/utils/jwt.js
export const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error parsing JWT:', error);
    return null;
  }
};

export const isTokenExpired = (token) => {
  try {
    const decoded = parseJwt(token);
    if (!decoded || !decoded.exp) {
      return true; // If there's no expiration, consider it expired
    }

    const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('Error checking token expiration:', error);
    return true;
  }
};

export const getTokenExpiration = (token) => {
  try {
    const decoded = parseJwt(token);
    if (!decoded || !decoded.exp) {
      return null;
    }

    return new Date(decoded.exp * 1000); // Convert seconds to milliseconds
  } catch (error) {
    console.error('Error getting token expiration:', error);
    return null;
  }
};

export const getUserIdFromToken = (token) => {
  try {
    const decoded = parseJwt(token);
    return decoded?.user_id || decoded?.sub || null;
  } catch (error) {
    console.error('Error getting user ID from token:', error);
    return null;
  }
};