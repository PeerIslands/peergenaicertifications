import { TypingIndicator } from '../TypingIndicator';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export default function TypingIndicatorExample() {
  const [visible, setVisible] = useState(true);

  return (
    <div className="space-y-4">
      <Button onClick={() => setVisible(!visible)}>
        {visible ? 'Hide' : 'Show'} Typing Indicator
      </Button>
      <TypingIndicator visible={visible} />
    </div>
  );
}