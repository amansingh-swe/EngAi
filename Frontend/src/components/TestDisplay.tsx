/**
 * Component for displaying generated test cases.
 */
import React from 'react';
import { CodeDisplay } from './CodeDisplay';

interface TestDisplayProps {
  tests: string;
}

export const TestDisplay: React.FC<TestDisplayProps> = ({ tests }) => {
  return <CodeDisplay title="Generated Test Cases" code={tests} language="python" />;
};


