import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Topic, Scope } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseTopicsReturn {
  topics: Topic[];
  loading: boolean;
  error: string | null;
  getTopics: (scope?: Scope) => Promise<Topic[]>;
  createTopic: (name: string, description?: string, scope?: Scope) => Promise<Topic | null>;
  updateTopic: (id: number, name: string, description?: string, scope?: Scope) => Promise<Topic | null>;
  deleteTopic: (id: number) => Promise<boolean>;
}

export const useTopics = (): UseTopicsReturn => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const getTopics = useCallback(async (scope: Scope = 'personal') => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_URL}/topics`, {
        params: { scope },
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      setTopics(response.data);
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'トピックの取得に失敗しました');
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const createTopic = useCallback(async (
    name: string,
    description?: string,
    scope: Scope = 'personal'
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        `${API_URL}/topics`,
        { name, description, scope },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      
      setTopics((prev) => [...prev, response.data]);
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'トピックの作成に失敗しました');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTopic = useCallback(async (
    id: number,
    name: string,
    description?: string,
    scope: Scope = 'personal'
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.put(
        `${API_URL}/topics/${id}`,
        { name, description, scope },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      
      setTopics((prev) => 
        prev.map((topic) => (topic.id === id ? response.data : topic))
      );
      
      return response.data;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'トピックの更新に失敗しました');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTopic = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    
    try {
      await axios.delete(`${API_URL}/topics/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      setTopics((prev) => prev.filter((topic) => topic.id !== id));
      return true;
    } catch (error: any) {
      setError(error.response?.data?.detail || 'トピックの削除に失敗しました');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    getTopics();
  }, [getTopics]);

  return {
    topics,
    loading,
    error,
    getTopics,
    createTopic,
    updateTopic,
    deleteTopic,
  };
};
