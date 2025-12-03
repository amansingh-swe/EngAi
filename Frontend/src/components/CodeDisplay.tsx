/**
 * Component for displaying generated code.
 */
import React from 'react';

interface CodeDisplayProps {
  title: string;
  code: string;
  language?: string;
}

export const CodeDisplay: React.FC<CodeDisplayProps> = ({ title, code, language = 'python' }) => {
  if (!code) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">{title}</h3>
      <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
        <pre className="text-sm text-gray-100 font-mono whitespace-pre-wrap">
          <code>{code}</code>
        </pre>
      </div>
      <div className="mt-2 flex justify-end">
        <button
          onClick={() => {
            navigator.clipboard.writeText(code);
          }}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Copy to Clipboard
        </button>
      </div>
    </div>
  );
};


