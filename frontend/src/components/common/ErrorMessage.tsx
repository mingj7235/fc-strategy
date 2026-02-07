interface ErrorMessageProps {
  message: string;
  type?: 'error' | 'warning' | 'info';
}

const ErrorMessage = ({ message, type = 'error' }: ErrorMessageProps) => {
  // Determine if this is a "user not found" error
  const isUserNotFound =
    message.includes('찾을 수 없습니다') ||
    message.includes('User not found') ||
    message.toLowerCase().includes('not found');

  // Debug log
  console.log('ErrorMessage - message:', message, 'isUserNotFound:', isUserNotFound);

  if (isUserNotFound) {
    return (
      <div className="bg-yellow-500/10 border-2 border-yellow-500/40 rounded-xl p-5 shadow-lg" role="alert">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
              <span className="text-2xl">🔍</span>
            </div>
          </div>
          <div className="flex-1">
            <h3 className="text-yellow-400 font-bold text-lg mb-1">유저를 찾을 수 없습니다</h3>
            <p className="text-gray-300 text-sm leading-relaxed">
              {message}
            </p>
            <div className="mt-3 text-xs text-gray-400 bg-dark-bg/50 rounded-lg p-3">
              <p className="mb-1">💡 <strong>도움말:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>닉네임 철자를 다시 확인해주세요</li>
                <li>대소문자와 특수문자를 정확히 입력했는지 확인하세요</li>
                <li>FC Online에서 실제로 사용중인 닉네임인지 확인하세요</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Default error styling
  const styles = {
    error: {
      bg: 'bg-accent-danger/10',
      border: 'border-accent-danger/30',
      text: 'text-accent-danger',
      icon: '❌',
      title: '오류'
    },
    warning: {
      bg: 'bg-yellow-500/10',
      border: 'border-yellow-500/30',
      text: 'text-yellow-400',
      icon: '⚠️',
      title: '경고'
    },
    info: {
      bg: 'bg-blue-500/10',
      border: 'border-blue-500/30',
      text: 'text-blue-400',
      icon: 'ℹ️',
      title: '안내'
    }
  };

  const style = styles[type];

  return (
    <div className={`${style.bg} border ${style.border} ${style.text} px-4 py-3 rounded-lg relative shadow-dark`} role="alert">
      <strong className="font-bold">{style.icon} {style.title}: </strong>
      <span className="block sm:inline">{message}</span>
    </div>
  );
};

export default ErrorMessage;
