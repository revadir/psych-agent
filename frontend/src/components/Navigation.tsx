import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

interface NavigationProps {
  user?: {
    email: string;
    name?: string;
  };
}

const Navigation: React.FC<NavigationProps> = ({ user }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/', icon: '🏠' },
    { name: 'Features', path: '/features', icon: '⚡' },
    { name: 'Scribe', path: '/scribe', icon: '📝' },
    { name: 'Chat', path: '/chat', icon: '💬' },
    { name: 'Admin', path: '/admin', icon: '⚙️' },
  ];

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between">
        {/* Logo and Navigation */}
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">PA</span>
            </div>
            <span className="text-gray-900 font-semibold text-lg">Psych Agent</span>
          </div>
          
          <div className="flex space-x-6">
            {navItems.map((item) => (
              <button
                key={item.name}
                onClick={() => navigate(item.path)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* User Avatar */}
        <div className="flex items-center space-x-4">
          {user && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                </span>
              </div>
              <span className="text-gray-700 text-sm hidden md:block">
                {user.name || user.email}
              </span>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
