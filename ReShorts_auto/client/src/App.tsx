import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Search } from './pages/Search';
import { VideoManager } from './pages/VideoManager';
import { Settings } from './pages/Settings';
import { Status } from './pages/Status';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="search" element={<Search />} />
          <Route path="videos" element={<VideoManager />} />
          <Route path="settings" element={<Settings />} />
          <Route path="status" element={<Status />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
