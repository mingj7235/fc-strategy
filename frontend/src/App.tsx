import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';
import HomePage from './pages/HomePage';
import UserDashboard from './pages/UserDashboard';
import MatchDetailPage from './pages/MatchDetailPage';
import ShotAnalysisPage from './pages/ShotAnalysisPage';
import StyleAnalysisPage from './pages/StyleAnalysisPage';
import PowerRankingsPage from './pages/PowerRankingsPage';
import SetPieceAnalysisPage from './pages/SetPieceAnalysisPage';
import DefenseAnalysisPage from './pages/DefenseAnalysisPage';
import PassVarietyAnalysisPage from './pages/PassVarietyAnalysisPage';
import ShootingQualityAnalysisPage from './pages/ShootingQualityAnalysisPage';
import ControllerAnalysisPage from './pages/ControllerAnalysisPage';
import SkillGapPage from './pages/SkillGapPage';
import SquadROIPage from './pages/SquadROIPage';
import FormCyclePage from './pages/FormCyclePage';
import RankerGapPage from './pages/RankerGapPage';
import HabitLoopPage from './pages/HabitLoopPage';
import OpponentTypesPage from './pages/OpponentTypesPage';
import OpponentScoutPage from './pages/OpponentScoutPage';

function AppContent() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  // Check if current page is HomePage
  const isHomePage = location.pathname === '/';

  return (
    <div className="flex min-h-screen bg-dark-bg">
      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onToggle={toggleSidebar} />

      {/* Main Content Area */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/user/:ouid" element={<UserDashboard />} />
            <Route path="/match/:matchId" element={<MatchDetailPage />} />
            <Route path="/user/:ouid/analysis/shots" element={<ShotAnalysisPage />} />
            <Route path="/user/:ouid/analysis/style" element={<StyleAnalysisPage />} />
            <Route path="/user/:ouid/power-rankings" element={<PowerRankingsPage />} />
            <Route path="/user/:ouid/analysis/set-pieces" element={<SetPieceAnalysisPage />} />
            <Route path="/user/:ouid/analysis/defense" element={<DefenseAnalysisPage />} />
            <Route path="/user/:ouid/analysis/pass-variety" element={<PassVarietyAnalysisPage />} />
            <Route path="/user/:ouid/analysis/shooting-quality" element={<ShootingQualityAnalysisPage />} />
            <Route path="/user/:ouid/analysis/controller" element={<ControllerAnalysisPage />} />
            {/* Phase 1 & 2 Advanced Analysis */}
            <Route path="/user/:ouid/analysis/skill-gap" element={<SkillGapPage />} />
            <Route path="/user/:ouid/analysis/player-contribution" element={<SquadROIPage />} />
            <Route path="/user/:ouid/analysis/form-cycle" element={<FormCyclePage />} />
            <Route path="/user/:ouid/analysis/ranker-gap" element={<RankerGapPage />} />
            <Route path="/user/:ouid/analysis/habit-loop" element={<HabitLoopPage />} />
            <Route path="/user/:ouid/analysis/opponent-types" element={<OpponentTypesPage />} />
            <Route path="/opponent-scout" element={<OpponentScoutPage />} />
          </Routes>
        </div>
        {/* Only show Footer if NOT on HomePage */}
        {!isHomePage && <Footer />}
      </div>
    </div>
  );
}

function App() {
  console.log('🚀 App component rendering...');

  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
