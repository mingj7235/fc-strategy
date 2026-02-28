import { useState, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';
import ErrorBoundary from './components/common/ErrorBoundary';
import HomePage from './pages/HomePage';

// Lazy load all pages except HomePage (shown on initial visit)
const UserDashboard = lazy(() => import('./pages/UserDashboard'));
const MatchDetailPage = lazy(() => import('./pages/MatchDetailPage'));
const ShotAnalysisPage = lazy(() => import('./pages/ShotAnalysisPage'));
const StyleAnalysisPage = lazy(() => import('./pages/StyleAnalysisPage'));
const PowerRankingsPage = lazy(() => import('./pages/PowerRankingsPage'));
const SetPieceAnalysisPage = lazy(() => import('./pages/SetPieceAnalysisPage'));
const DefenseAnalysisPage = lazy(() => import('./pages/DefenseAnalysisPage'));
const PassVarietyAnalysisPage = lazy(() => import('./pages/PassVarietyAnalysisPage'));
const ShootingQualityAnalysisPage = lazy(() => import('./pages/ShootingQualityAnalysisPage'));
const ControllerAnalysisPage = lazy(() => import('./pages/ControllerAnalysisPage'));
const SkillGapPage = lazy(() => import('./pages/SkillGapPage'));
const SquadROIPage = lazy(() => import('./pages/SquadROIPage'));
const FormCyclePage = lazy(() => import('./pages/FormCyclePage'));
const RankerGapPage = lazy(() => import('./pages/RankerGapPage'));
const HabitLoopPage = lazy(() => import('./pages/HabitLoopPage'));
const OpponentTypesPage = lazy(() => import('./pages/OpponentTypesPage'));
const OpponentScoutPage = lazy(() => import('./pages/OpponentScoutPage'));

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="animate-spin rounded-full h-8 w-8 border-2 border-accent-primary border-t-transparent" />
    </div>
  );
}

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
          <ErrorBoundary>
          <Suspense fallback={<PageLoader />}>
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
          </Suspense>
          </ErrorBoundary>
        </div>
        {/* Only show Footer if NOT on HomePage */}
        {!isHomePage && <Footer />}
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
