'use client';

import { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import Dashboard from '@/components/Dashboard';
import { User } from '@supabase/auth-helpers-nextjs';

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = createClientComponentClient();

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      setLoading(false);
    };

    getUser();
  }, [supabase]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading GrandFLOW...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center space-y-6">
            <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-2xl font-bold text-white">G</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Welcome to GrandFLOW</h1>
            <p className="text-gray-600">
              Your comprehensive health monitoring and concierge services platform
            </p>
            <div className="space-y-3">
              <button
                onClick={() => supabase.auth.signInWithOAuth({ provider: 'google' })}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                Sign in with Google
              </button>
              <button
                onClick={() => supabase.auth.signInWithOAuth({ provider: 'github' })}
                className="w-full bg-gray-800 hover:bg-gray-900 text-white font-medium py-3 px-4 rounded-lg transition-colors"
              >
                Sign in with GitHub
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Dashboard 
      userId={user.id} 
      userRole="senior" // This would be determined from user metadata
    />
  );
}
