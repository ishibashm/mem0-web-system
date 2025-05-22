import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { Provider } from '@/types';

interface ApiSettingsPopupProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function ApiSettingsPopup({ isOpen, setIsOpen }: ApiSettingsPopupProps) {
  const { user, updateUser } = useAuth();
  const [mem0ApiKey, setMem0ApiKey] = useState('');
  const [llmApiKey, setLlmApiKey] = useState('');
  const [provider, setProvider] = useState<Provider>('openai');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      setMem0ApiKey(user.mem0_api_key || '');
      setLlmApiKey(user.llm_api_key || '');
      setProvider((user.llm_provider as Provider) || 'openai');
    }
  }, [user, isOpen]);

  const handleSave = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/me`,
        {
          mem0_api_key: mem0ApiKey || null,
          llm_api_key: llmApiKey || null,
          llm_provider: provider,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      updateUser(response.data);
      setIsOpen(false);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'APIキーの更新に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>API設定</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="mem0-api-key" className="text-right">
              Mem0 APIキー
            </Label>
            <Input
              id="mem0-api-key"
              value={mem0ApiKey}
              onChange={(e) => setMem0ApiKey(e.target.value)}
              placeholder="mem0_..."
              className="col-span-3"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="llm-provider" className="text-right">
              LLMプロバイダー
            </Label>
            <Select value={provider} onValueChange={(value) => setProvider(value as Provider)}>
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="プロバイダーを選択" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openai">OpenAI</SelectItem>
                <SelectItem value="anthropic">Anthropic</SelectItem>
                <SelectItem value="cohere">Cohere</SelectItem>
                <SelectItem value="groq">Groq</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="llm-api-key" className="text-right">
              LLM APIキー
            </Label>
            <Input
              id="llm-api-key"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              placeholder={
                provider === 'openai'
                  ? 'sk-...'
                  : provider === 'anthropic'
                  ? 'sk-ant-...'
                  : provider === 'cohere'
                  ? 'co-...'
                  : 'gsk_...'
              }
              className="col-span-3"
            />
          </div>
        </div>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            キャンセル
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            {loading ? '保存中...' : '保存'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
