import React from 'react';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL!,
  process.env.REACT_APP_SUPABASE_ANON_KEY!
);

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-4xl font-bold">S.T.A.F.F. Bot Dashboard</h1>
      <p>Pannello Admin per gestione ticket Red Empire</p>
    </div>
  );
}

export default App;