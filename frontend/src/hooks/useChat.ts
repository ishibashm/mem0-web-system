import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import { Message, Memory, Provider, Scope } from '@/types';
import { format } from 'date-fns';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface UseChatProps {
  userId: string;
  mem0ApiKey?: string;
  llmApiKey?: string;
  provider?: Provider;
  scope?: Scope;
  topicId?: number;
}

interface UseChatReturn {
  messages: Message[];
  memories: Memory[];
  thinking: boolean;
  sendMessage: (content: string, image?: { type: string; data: string }) => Promise<void>;
}

export const useChat = ({
  userId,
  mem0ApiKey,
  llmApiKey,
  provider = 'openai',
  scope = 'personal',
  topicId,
}: UseChatProps): UseChatReturn => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [thinking, setThinking] = useState(false);

  const fetchMemories = useCallback(async () => {
    if (!mem0ApiKey) return;

    try {
      const response = await axios.get(`${API_URL}/memories`, {
        params: {
          scope,
          topic_id: topicId,
        },
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      const formattedMemories: Memory[] = response.data.map((memory: any) => ({
        id: memory.id,
        content: memory.content,
        timestamp: format(new Date(memory.created_at), 'yyyy-MM-dd HH:mm'),
        tags: memory.tags.map((tag: any) => tag.name),
      }));

      setMemories(formattedMemories);
    } catch (error) {
      console.error('メモリの取得に失敗しました', error);
    }
  }, [mem0ApiKey, scope, topicId]);

  useEffect(() => {
    fetchMemories();
  }, [fetchMemories]);

  const sendMessage = useCallback(
    async (content: string, image?: { type: string; data: string }) => {
      if (!content.trim() && !image) return;

      setThinking(true);

      const userMessage: Message = {
        id: uuidv4(),
        content,
        role: 'user',
        timestamp: format(new Date(), 'yyyy-MM-dd HH:mm'),
        image: image?.data,
      };

      setMessages((prev) => [...prev, userMessage]);

      try {
        const apiMessages = messages
          .concat(userMessage)
          .map(({ role, content, image }) => ({
            role,
            content,
            image_url: image,
          }));

        const response = await axios.post(
          `${API_URL}/api/v1/chat`,
          {
            messages: apiMessages,
            user_id: userId,
            scope,
            topic_id: topicId,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
          }
        );

        const assistantMessage: Message = {
          id: uuidv4(),
          content: response.data.message.content,
          role: 'assistant',
          timestamp: format(new Date(), 'yyyy-MM-dd HH:mm'),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        fetchMemories();
      } catch (error) {
        console.error('メッセージの送信に失敗しました', error);
        
        const errorMessage: Message = {
          id: uuidv4(),
          content: 'メッセージの送信中にエラーが発生しました。APIキーが正しく設定されているか確認してください。',
          role: 'assistant',
          timestamp: format(new Date(), 'yyyy-MM-dd HH:mm'),
        };

        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setThinking(false);
      }
    },
    [messages, userId, scope, topicId, fetchMemories]
  );

  return {
    messages,
    memories,
    thinking,
    sendMessage,
  };
};
