import React from 'react';

interface UserAvatarProps {
  email?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

const sizeClasses = {
  sm: 'w-8 h-8 text-sm',
  md: 'w-10 h-10 text-base',
  lg: 'w-12 h-12 text-lg',
  xl: 'w-16 h-16 text-xl',
};

// Predefined color palette for avatars
const colorPalette = [
  'bg-indigo-500 dark:bg-indigo-600',
  'bg-blue-500 dark:bg-blue-600',
  'bg-green-500 dark:bg-green-600',
  'bg-yellow-500 dark:bg-yellow-600',
  'bg-orange-500 dark:bg-orange-600',
  'bg-red-500 dark:bg-red-600',
  'bg-purple-500 dark:bg-purple-600',
  'bg-pink-500 dark:bg-pink-600',
  'bg-teal-500 dark:bg-teal-600',
  'bg-cyan-500 dark:bg-cyan-600',
];

const UserAvatar: React.FC<UserAvatarProps> = ({
  email,
  size = 'md',
  className = ''
}) => {
  // Extract initials from email
  const getInitials = (email: string | undefined): string => {
    if (!email) return 'U'; // Fallback to 'U' if no email

    const [username] = email.split('@');
    if (!username) return 'U'; // Fallback if email format is invalid

    // Take first 2 characters of username and convert to uppercase
    const initials = username.substring(0, 2).toUpperCase();
    return initials;
  };

  const initials = getInitials(email);

  // Determine color based on the initials
  const getColorClass = (initials: string): string => {
    if (!initials) return colorPalette[0]; // Default color if no initials

    // Create a hash from the initials to determine color index
    let hash = 0;
    for (let i = 0; i < initials.length; i++) {
      hash = initials.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Use the hash to pick a color from the palette
    const colorIndex = Math.abs(hash) % colorPalette.length;
    return colorPalette[colorIndex];
  };

  const colorClass = getColorClass(initials);

  return (
    <div
      className={`
        ${sizeClasses[size]}
        ${colorClass}
        rounded-full flex items-center justify-center
        text-white font-semibold
        shadow-md
        ${className}
      `}
      aria-label={`User avatar for ${email || 'Unknown User'}`}
    >
      {initials}
    </div>
  );
};

export default UserAvatar;