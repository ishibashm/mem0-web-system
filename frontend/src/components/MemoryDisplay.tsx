import { Memory } from '@/types';
import { format } from 'date-fns';

interface MemoryDisplayProps {
  memories: Memory[];
}

export default function MemoryDisplay({ memories }: MemoryDisplayProps) {
  if (memories.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        メモリがありません。チャットを開始すると、ここにメモリが表示されます。
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {memories.map((memory) => (
        <div
          key={memory.id}
          className="p-3 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          <p className="text-sm whitespace-pre-wrap">{memory.content}</p>
          <div className="mt-2 flex justify-between items-center">
            <div className="text-xs text-gray-500">{memory.timestamp}</div>
            <div className="flex flex-wrap gap-1">
              {memory.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
