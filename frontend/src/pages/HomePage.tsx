import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchUser } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorMessage from '../components/common/ErrorMessage';

// Buy Me a Coffee configuration
const BUYMEACOFFEE_USERNAME = 'joshuara7235';

const HomePage = () => {
  console.log('🏠 HomePage component rendering');

  const [nickname, setNickname] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!nickname.trim()) {
      setError('닉네임을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      console.log('Searching for user:', nickname);
      const user = await searchUser(nickname);
      console.log('User found:', user);
      navigate(`/user/${user.ouid}`);
    } catch (err: any) {
      console.error('Search error:', err);
      console.error('Error response:', err.response);
      console.error('Error response data:', err.response?.data);
      console.error('Error response status:', err.response?.status);

      // Handle specific error messages
      const errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || '유저를 찾을 수 없습니다.';

      console.log('Extracted error message:', errorMessage);

      // Make error message more user-friendly
      if (
        errorMessage.includes('찾을 수 없습니다') ||
        errorMessage.includes('User not found') ||
        errorMessage.toLowerCase().includes('not found') ||
        err.response?.status === 404
      ) {
        setError(`"${nickname}" 닉네임을 가진 유저를 찾을 수 없습니다. 닉네임을 다시 확인해주세요.`);
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-dark-card to-dark-bg flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-4">
            ⚽ FC Strategy Coach
          </h1>
          <p className="text-xl text-gray-300">
            당신의 플레이를 분석하는 AI 전술 코치
          </p>
        </div>

        <div className="bg-dark-card rounded-lg shadow-dark-lg border border-dark-border p-8">
          <form onSubmit={handleSearch}>
            <div className="mb-6">
              <label htmlFor="nickname" className="block text-sm font-medium text-gray-300 mb-2">
                FC Online 닉네임
              </label>
              <input
                type="text"
                id="nickname"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="닉네임을 입력하세요"
                className="w-full px-4 py-3 bg-dark-bg border border-dark-border text-white rounded-lg focus:ring-2 focus:ring-accent-primary focus:border-transparent transition-all placeholder-gray-500"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="mb-4">
                <ErrorMessage message={error} />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-accent-primary to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-600 hover:to-accent-primary focus:outline-none focus:ring-2 focus:ring-accent-primary focus:ring-offset-2 focus:ring-offset-dark-card disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02]"
            >
              {loading ? '검색 중...' : '전적 분석하기'}
            </button>
          </form>

          {loading && (
            <div className="mt-6">
              <LoadingSpinner />
            </div>
          )}
        </div>

        {/* Footer Info */}
        <div className="mt-8 text-center space-y-6">
          {/* Powered by */}
          <div>
            <p className="text-sm text-gray-400 mb-3">
              Powered by{' '}
              <a
                href="https://openapi.nexon.com/ko/game/fconline/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-primary hover:text-blue-400 transition-colors font-semibold"
              >
                Nexon Open API
              </a>
            </p>
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
          <p className="text-xs text-gray-500 max-w-md mx-auto">
            이 프로젝트가 유용하셨다면 커피 한 잔으로 응원해주세요! ☕
            <br />
            여러분의 후원이 더 나은 분석 기능 개발에 큰 힘이 됩니다.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
