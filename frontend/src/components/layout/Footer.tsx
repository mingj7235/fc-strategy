import React from 'react';

// Buy Me a Coffee configuration
const BUYMEACOFFEE_USERNAME = 'joshuara7235';

const Footer: React.FC = () => {
  return (
    <>
      <footer className="bg-gradient-to-b from-dark-card to-dark-bg border-t border-dark-border py-8 px-4 mt-12">
        <div className="max-w-7xl mx-auto">
          {/* Main Content */}
          <div className="flex flex-col items-center gap-6">
            {/* Powered by */}
            <div className="text-center">
              <div className="text-sm text-gray-400 mb-2">
                Powered by{' '}
                <a
                  href="https://openapi.nexon.com/ko/game/fconline/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent-primary hover:text-blue-400 transition-colors font-semibold"
                >
                  Nexon Open API
                </a>
              </div>
              <div className="text-xs text-gray-500 flex items-center justify-center gap-2">
                <span>⚽</span>
                <span>Created with passion by</span>
                <span className="text-white font-bold">ZinedineZidane05</span>
                <span>⚽</span>
              </div>
            </div>

            {/* Buy Me a Coffee Button - Official */}
            <a
              href={`https://www.buymeacoffee.com/${BUYMEACOFFEE_USERNAME}`}
              target="_blank"
              rel="noopener noreferrer"
              className="group relative px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 inline-flex items-center gap-2"
            >
              <span className="text-2xl">☕</span>
              <span>Buy Me a Coffee</span>
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-xl transition-opacity"></div>
            </a>

            {/* Description */}
            <div className="text-center max-w-2xl">
              <p className="text-xs text-gray-500">
                이 프로젝트가 유용하셨다면 커피 한 잔으로 응원해주세요! ☕
                <br />
                여러분의 후원이 더 나은 분석 기능 개발에 큰 힘이 됩니다.
              </p>
            </div>

            {/* Copyright */}
            <div className="text-xs text-gray-600 text-center border-t border-dark-border pt-4 w-full">
              <p>© 2026 FC Strategy. All rights reserved.</p>
              <p className="mt-1">
                This project is not affiliated with EA SPORTS or Nexon.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
};

export default Footer;
