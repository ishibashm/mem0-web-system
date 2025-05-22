import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';
import { useUserSettings } from '@/hooks/useUserSettings';
import { UserSettings } from '@/types';

interface UserSettingsDialogProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function UserSettingsDialog({ isOpen, setIsOpen }: UserSettingsDialogProps) {
  const { settings, loading, error, getUserSettings, updateUserSettings } = useUserSettings();
  const [formData, setFormData] = useState<Partial<UserSettings>>({
    memory_retention_days: 90,
    max_memories_per_topic: 1000,
    default_search_type: 'vector',
    default_scope: 'personal',
    embedding_model: 'text-embedding-ada-002',
    language_preference: 'ja'
  });

  useEffect(() => {
    if (isOpen) {
      getUserSettings();
    }
  }, [isOpen, getUserSettings]);

  useEffect(() => {
    if (settings) {
      setFormData({
        memory_retention_days: settings.memory_retention_days,
        max_memories_per_topic: settings.max_memories_per_topic,
        default_search_type: settings.default_search_type,
        default_scope: settings.default_scope,
        embedding_model: settings.embedding_model,
        language_preference: settings.language_preference
      });
    }
  }, [settings]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'number' ? parseInt(value) : value
    });
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSave = async () => {
    const result = await updateUserSettings(formData);
    if (result) {
      setIsOpen(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>ユーザー設定</DialogTitle>
        </DialogHeader>
        
        {loading ? (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="memory_retention_days" className="text-right">
                メモリ保持期間（日）
              </Label>
              <Input
                id="memory_retention_days"
                name="memory_retention_days"
                type="number"
                value={formData.memory_retention_days}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="max_memories_per_topic" className="text-right">
                トピックごとの最大メモリ数
              </Label>
              <Input
                id="max_memories_per_topic"
                name="max_memories_per_topic"
                type="number"
                value={formData.max_memories_per_topic}
                onChange={handleInputChange}
                className="col-span-3"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="default_search_type" className="text-right">
                デフォルト検索タイプ
              </Label>
              <Select
                value={formData.default_search_type}
                onValueChange={(value) => handleSelectChange('default_search_type', value)}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="検索タイプを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="keyword">キーワード検索</SelectItem>
                  <SelectItem value="vector">ベクトル検索</SelectItem>
                  <SelectItem value="time">時系列検索</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="default_scope" className="text-right">
                デフォルトスコープ
              </Label>
              <Select
                value={formData.default_scope}
                onValueChange={(value) => handleSelectChange('default_scope', value)}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="スコープを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="personal">個人</SelectItem>
                  <SelectItem value="project">プロジェクト</SelectItem>
                  <SelectItem value="team">チーム</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="embedding_model" className="text-right">
                埋め込みモデル
              </Label>
              <Select
                value={formData.embedding_model}
                onValueChange={(value) => handleSelectChange('embedding_model', value)}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="埋め込みモデルを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="text-embedding-ada-002">OpenAI Ada 002</SelectItem>
                  <SelectItem value="text-embedding-3-small">OpenAI Embedding 3 Small</SelectItem>
                  <SelectItem value="text-embedding-3-large">OpenAI Embedding 3 Large</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="language_preference" className="text-right">
                言語設定
              </Label>
              <Select
                value={formData.language_preference}
                onValueChange={(value) => handleSelectChange('language_preference', value)}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="言語を選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ja">日本語</SelectItem>
                  <SelectItem value="en">英語</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )}
        
        {error && <p className="text-red-500 text-sm">{error}</p>}
        
        <DialogFooter>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            キャンセル
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            保存
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
