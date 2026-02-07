import React, { useState, useMemo } from 'react';

interface PlayerAvatarProps {
  spid?: number;
  imageUrl?: string;
  playerName?: string;
  size?: number;
  className?: string;
}

const CDN = 'https://fo4.dn.nexoncdn.co.kr/live/externalAssets/common/playersAction';

const GRADIENTS = [
  ['#3b5bdb', '#1971c2'],
  ['#7048e8', '#ae3ec9'],
  ['#0ca678', '#087f5b'],
  ['#e8590c', '#c92a2a'],
  ['#1098ad', '#0b7285'],
  ['#f08c00', '#d9480f'],
  ['#5c7cfa', '#364fc7'],
  ['#cc5de8', '#9c36b5'],
];

function nameToGradient(name: string): [string, string] {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  }
  const pair = GRADIENTS[hash % GRADIENTS.length];
  return [pair[0], pair[1]];
}

interface SilhouetteAvatarProps {
  name: string;
  size: number;
  className?: string;
}

const SilhouetteAvatar: React.FC<SilhouetteAvatarProps> = ({ name, size, className = '' }) => {
  const [from, to] = nameToGradient(name);
  const borderRadius = Math.round(size * 0.12);

  return (
    <div
      className={`flex items-center justify-center select-none flex-shrink-0 overflow-hidden ${className}`}
      style={{
        width: size,
        height: size,
        borderRadius,
        background: `linear-gradient(160deg, ${from}, ${to})`,
        boxShadow: `inset 0 0 0 1px rgba(255,255,255,0.10)`,
      }}
      title={name}
    >
      {/* Football player upper-body silhouette */}
      <svg
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: '88%', height: '88%' }}
      >
        {/* Head */}
        <circle cx="50" cy="24" r="16" fill="rgba(255,255,255,0.72)" />
        {/* Neck */}
        <rect x="44" y="38" width="12" height="8" rx="3" fill="rgba(255,255,255,0.72)" />
        {/* Shoulders + torso (cut off at bottom) */}
        <path
          d="M16,58 L22,46 C28,38 38,44 50,44 C62,44 72,38 78,46 L84,58
             C84,58 80,72 80,100 L20,100 C20,72 16,58 16,58 Z"
          fill="rgba(255,255,255,0.72)"
        />
        {/* Left arm */}
        <path
          d="M22,46 L6,60 L12,68 L28,52 Z"
          fill="rgba(255,255,255,0.72)"
        />
        {/* Right arm */}
        <path
          d="M78,46 L94,60 L88,68 L72,52 Z"
          fill="rgba(255,255,255,0.72)"
        />
      </svg>
    </div>
  );
};

/**
 * Player image with multi-level fallback:
 *   1. imageUrl / playersAction/p{spid}.png  (primary)
 *   2. playersAction/p{100*1e6 + baseId}.png (ICON TM)
 *   3. playersAction/p{101*1e6 + baseId}.png (ICON)
 *   4. Player silhouette avatar (gradient bg + deterministic color)
 */
const PlayerAvatar: React.FC<PlayerAvatarProps> = ({
  spid,
  imageUrl,
  playerName = '',
  size = 40,
  className = '',
}) => {
  const fallbackUrls = useMemo(() => {
    const primary = imageUrl || (spid ? `${CDN}/p${spid}.png` : null);
    if (!spid) return primary ? [primary] : [];

    const baseId = spid % 1000000;
    const urls: string[] = [];
    if (primary) urls.push(primary);
    urls.push(`${CDN}/p${100 * 1000000 + baseId}.png`);
    urls.push(`${CDN}/p${101 * 1000000 + baseId}.png`);
    return urls;
  }, [spid, imageUrl]);

  const [idx, setIdx] = useState(0);
  const [allFailed, setAllFailed] = useState(false);

  const handleError = () => {
    if (idx < fallbackUrls.length - 1) {
      setIdx(i => i + 1);
    } else {
      setAllFailed(true);
    }
  };

  if (allFailed || fallbackUrls.length === 0) {
    return <SilhouetteAvatar name={playerName} size={size} className={className} />;
  }

  return (
    <img
      src={fallbackUrls[idx]}
      alt={playerName}
      width={size}
      height={size}
      loading="lazy"
      className={`object-contain ${className}`}
      style={{ width: size, height: size }}
      onError={handleError}
    />
  );
};

export default PlayerAvatar;
