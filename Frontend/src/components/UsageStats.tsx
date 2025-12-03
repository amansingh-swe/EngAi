/**
 * Component for displaying LLM usage statistics.
 */
import React, { useEffect, useState } from 'react';
import { api, UsageStats } from '../api/client';

export const UsageStatsComponent: React.FC = () => {
  const [stats, setStats] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getUsageStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load usage statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Usage Statistics</h3>
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Usage Statistics</h3>
        <p className="text-red-500">{error}</p>
        <button
          onClick={fetchStats}
          className="mt-2 text-primary-600 hover:text-primary-700 font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-gray-800">Usage Statistics</h3>
        <button
          onClick={fetchStats}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Total API Calls</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total_api_calls}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Input Tokens</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total_input_tokens.toLocaleString()}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Output Tokens</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total_output_tokens.toLocaleString()}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-1">Total Tokens</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total_tokens.toLocaleString()}</p>
        </div>
      </div>

      {stats.agents.length > 0 && (
        <div>
          <h4 className="text-lg font-semibold text-gray-700 mb-3">Per-Agent Statistics</h4>
          <div className="space-y-2">
            {stats.agents.map((agent) => (
              <div key={agent.agent_name} className="bg-gray-50 rounded-lg p-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium text-gray-800">{agent.agent_name}</span>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>{agent.total_api_calls} calls</span>
                    <span>{agent.total_tokens.toLocaleString()} tokens</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};


