import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-background-base">
      <Sidebar />
      <Header />
      
      <main className="ml-60 mt-16 p-2xl">
        <Outlet />
      </main>
    </div>
  );
};
