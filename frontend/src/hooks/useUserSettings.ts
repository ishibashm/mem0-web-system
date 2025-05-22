import { useState, useCallback } from 'react';
import axios from 'axios';
import { UserSettings } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseUserSettingsReturn {
  settings: UserSettings | null;
  loading: boolean;
  error: string | null;
  getUserSettings: () => Promise<UserSettings | null>;
  updateUserSettings: (settings: Partial<UserSettings>) => Promise<UserSettings | null>;
}

export const useUserSettings = (): UseUserSettingsReturn => {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getUserSettings = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_URL}/settings`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setSettings(response.data);
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || '設定の取得に失敗しました');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateUserSettings = useCallback(async (updatedSettings: Partial<UserSettings>) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.put(`${API_URL}/settings`, updatedSettings, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setSettings(response.data);
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || '設定の更新に失敗しました');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    settings,
    loading,
    error,
    getUserSettings,
    updateUserSettings
  };
};
