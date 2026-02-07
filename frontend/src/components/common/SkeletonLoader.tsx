import React from 'react';

// Base shimmer animation class
const shimmer = 'animate-pulse bg-dark-hover rounded';

/** Single-line text placeholder */
export const SkeletonText: React.FC<{ width?: string; height?: string; className?: string }> = ({
  width = 'w-full',
  height = 'h-4',
  className = '',
}) => (
  <div className={`${shimmer} ${width} ${height} ${className}`} />
);

/** Rectangular block placeholder */
export const SkeletonBlock: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`${shimmer} ${className}`} />
);

/** Match card skeleton - mirrors MatchCard layout */
export const MatchCardSkeleton: React.FC = () => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4">
    <div className="flex items-center justify-between">
      {/* Left: result + score */}
      <div className="flex items-center gap-4">
        <SkeletonBlock className="w-10 h-10 rounded-full" />
        <div className="space-y-2">
          <SkeletonText width="w-16" height="h-6" />
          <SkeletonText width="w-24" height="h-3" />
        </div>
      </div>

      {/* Center: score */}
      <SkeletonText width="w-20" height="h-8" />

      {/* Right: stats */}
      <div className="space-y-2 text-right">
        <SkeletonText width="w-24" height="h-3" />
        <SkeletonText width="w-20" height="h-3" />
      </div>
    </div>
  </div>
);

/** Stats card skeleton */
export const StatCardSkeleton: React.FC = () => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4">
    <SkeletonText width="w-24" height="h-3" className="mb-2" />
    <SkeletonText width="w-16" height="h-8" className="mb-1" />
    <SkeletonText width="w-32" height="h-3" />
  </div>
);

/** Match list skeleton - shows N placeholder cards */
export const MatchListSkeleton: React.FC<{ count?: number }> = ({ count = 5 }) => (
  <div className="space-y-3">
    {Array.from({ length: count }).map((_, i) => (
      <MatchCardSkeleton key={i} />
    ))}
  </div>
);

/** Dashboard overview stats skeleton */
export const DashboardOverviewSkeleton: React.FC = () => (
  <div className="space-y-6">
    {/* Record cards row */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <StatCardSkeleton key={i} />
      ))}
    </div>

    {/* Two-column stats row */}
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-dark-card border border-dark-border rounded-lg p-6 space-y-4">
        <SkeletonText width="w-40" height="h-5" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <SkeletonText width="w-24" height="h-3" />
            <div className="flex-1">
              <SkeletonBlock className="h-2 rounded-full" />
            </div>
            <SkeletonText width="w-10" height="h-3" />
          </div>
        ))}
      </div>
      <div className="bg-dark-card border border-dark-border rounded-lg p-6 space-y-4">
        <SkeletonText width="w-40" height="h-5" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex justify-between">
            <SkeletonText width="w-20" height="h-3" />
            <SkeletonText width="w-12" height="h-3" />
          </div>
        ))}
      </div>
    </div>
  </div>
);

/** Player card skeleton for rankings */
export const PlayerCardSkeleton: React.FC = () => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4 flex items-center gap-4">
    <SkeletonText width="w-8" height="h-8" className="rounded-full flex-shrink-0" />
    <SkeletonBlock className="w-12 h-12 rounded-lg flex-shrink-0" />
    <div className="flex-1 space-y-2">
      <SkeletonText width="w-32" height="h-4" />
      <SkeletonText width="w-20" height="h-3" />
    </div>
    <div className="text-right space-y-2">
      <SkeletonText width="w-16" height="h-6" />
      <SkeletonText width="w-12" height="h-3" />
    </div>
  </div>
);

