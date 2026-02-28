import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="relative">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-dark-border border-t-accent-primary"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="text-2xl">⚽</div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(LoadingSpinner);
