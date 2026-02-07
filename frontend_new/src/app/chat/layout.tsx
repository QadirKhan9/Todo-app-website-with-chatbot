// frontend/src/app/chat/layout.tsx
import { ReactNode } from 'react';

export default function ChatLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="h-screen flex flex-col">
      {children}
    </div>
  );
}