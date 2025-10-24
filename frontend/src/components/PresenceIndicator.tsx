import React from 'react';
import { Users } from 'lucide-react';

interface PresenceIndicatorProps {
  viewers: string[];
  className?: string;
}

const PresenceIndicator: React.FC<PresenceIndicatorProps> = ({ viewers, className = '' }) => {
  if (viewers.length === 0) return null;

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className="flex items-center bg-green-50 border border-green-200 rounded-lg px-3 py-1.5">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Users className="w-4 h-4 text-green-600" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
          </div>
          <span className="text-sm font-medium text-green-700">
            {viewers.length} {viewers.length === 1 ? 'viewer' : 'viewers'} online
          </span>
        </div>
      </div>
      
      {/* User avatars */}
      <div className="flex -space-x-2">
        {viewers.slice(0, 3).map((viewerId, index) => (
          <div
            key={viewerId}
            className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 
                     border-2 border-white flex items-center justify-center text-white text-xs font-medium"
            title={`Viewer ${index + 1}`}
          >
            {String.fromCharCode(65 + index)}
          </div>
        ))}
        {viewers.length > 3 && (
          <div
            className="w-8 h-8 rounded-full bg-gray-200 border-2 border-white 
                     flex items-center justify-center text-gray-600 text-xs font-medium"
          >
            +{viewers.length - 3}
          </div>
        )}
      </div>
    </div>
  );
};

export default PresenceIndicator;
