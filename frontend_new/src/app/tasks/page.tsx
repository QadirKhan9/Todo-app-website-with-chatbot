import { redirect } from 'next/navigation';

// This page redirects to the dashboard tasks page
export default function TasksPage() {
  redirect('/dashboard/tasks');
}