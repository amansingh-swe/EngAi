/**
 * Aman singh(67401334)
 * Sanmith Kurian (22256557)
 * Yash Agarwal (35564877)
 * Swapnil Nagras (26761683)
 * 
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


