import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Settings, Send, Paperclip, Search, User } from 'lucide-react';
import ApiSettingsPopup from './ApiSettingsPopup';
import UserSettingsDialog from './UserSettingsDialog';
import MemoryDisplay from './MemoryDisplay';
import { v4 as uuidv4 } from 'uuid';
import { Scope, Topic } from '@/types';
import { useTopics } from '@/hooks/useTopics';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

interface ChatProps {
  initialScope?: Scope;
  initialTopicId?: number;
}

export default function Chat({ initialScope = 'personal', initialTopicId }: ChatProps) {
  const { user } = useAuth();
  const [input, setInput] = useState('');
  const [isApiSettingsOpen, setIsApiSettingsOpen] = useState(false);
  const [isUserSettingsOpen, setIsUserSettingsOpen] = useState(false);
  const [userId] = useState(uuidv4());
  const [scope, setScope] = useState<Scope>(
    user?.user_settings?.default_scope as Scope || initialScope
  );
  const [selectedTopicId, setSelectedTopicId] = useState<number | undefined>(initialTopicId);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [imageData, setImageData] = useState<{ type: string; data: string } | null>(null);
  const { topics, getTopics } = useTopics();

  const mem0ApiKey = user?.mem0_api_key || '';
  const llmApiKey = user?.llm_api_key || '';
  const provider = (user?.llm_provider || 'openai') as any;

  const { messages, memories, thinking, sendMessage } = useChat({
    userId,
    mem0ApiKey,
    llmApiKey,
    provider,
    scope,
    topicId: selectedTopicId
  });

  useEffect(() => {
    getTopics();
  }, [getTopics]);

  useEffect(() => {
    if (user?.user_settings?.default_scope) {
      setScope(user.user_settings.default_scope as Scope);
    }
  }, [user?.user_settings]);

  const handleSendMessage = () => {
    if (input.trim() || imageData) {
      sendMessage(input, imageData || undefined);
      setInput('');
      setImageData(null);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => {
        setImageData({
          type: file.type,
          data: reader.result as string,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen">
      <div className="flex justify-between items-center p-4 border-b">
        <h1 className="text-xl font-bold">Mem0 チャット</h1>
        <div className="flex items-center space-x-2">
          <Select value={scope} onValueChange={(value) => setScope(value as Scope)}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="スコープを選択" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="personal">個人</SelectItem>
              <SelectItem value="project">プロジェクト</SelectItem>
              <SelectItem value="team">チーム</SelectItem>
            </SelectContent>
          </Select>
          
          <Select 
            value={selectedTopicId?.toString() || ''} 
            onValueChange={(value) => setSelectedTopicId(value ? parseInt(value) : undefined)}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="トピックを選択" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">すべて</SelectItem>
              {topics.map((topic) => (
                <SelectItem key={topic.id} value={topic.id.toString()}>
                  {topic.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button variant="ghost" size="icon" onClick={() => setIsUserSettingsOpen(true)}>
            <User className="h-5 w-5" />
          </Button>
          
          <Button variant="ghost" size="icon" onClick={() => setIsApiSettingsOpen(true)}>
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 flex flex-col">
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  >
                    {message.image && (
                      <div className="mb-2">
                        <img
                          src={message.image}
                          alt="ユーザーアップロード"
                          className="max-w-full rounded"
                        />
                      </div>
                    )}
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    <div className="text-xs opacity-70 mt-1">{message.timestamp}</div>
                  </div>
                </div>
              ))}
              {thinking && (
                <div className="flex justify-start">
                  <div className="max-w-[80%] rounded-lg p-3 bg-gray-200 dark:bg-gray-700">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" />
                      <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce [animation-delay:0.2s]" />
                      <div className="w-2 h-2 rounded-full bg-gray-500 animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>

          <div className="p-4 border-t">
            {imageData && (
              <div className="mb-2 relative">
                <img
                  src={imageData.data}
                  alt="プレビュー"
                  className="h-20 rounded"
                />
                <button
                  className="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1"
                  onClick={() => setImageData(null)}
                >
                  ✕
                </button>
              </div>
            )}
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => fileInputRef.current?.click()}
              >
                <Paperclip className="h-5 w-5" />
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Button>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="メッセージを入力..."
                className="flex-1"
              />
              <Button onClick={handleSendMessage} disabled={thinking}>
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>

        <div className="w-80 border-l p-4 hidden md:block">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-semibold">メモリ</h2>
            <Button variant="ghost" size="sm">
              <Search className="h-4 w-4 mr-2" />
              検索
            </Button>
          </div>
          <MemoryDisplay memories={memories} />
        </div>
      </div>

      <ApiSettingsPopup isOpen={isApiSettingsOpen} setIsOpen={setIsApiSettingsOpen} />
      <UserSettingsDialog isOpen={isUserSettingsOpen} setIsOpen={setIsUserSettingsOpen} />
    </div>
  );
}
