/**
 * Aman singh(67401334)
 * Sanmith Kurian (22256557)
 * Yash Agarwal (35564877)
 * Swapnil Nagras (26761683)
 * 
 * Form component for inputting software description and requirements.
 */
import React, { useState } from 'react';

interface SoftwareDescriptionFormProps {
  onSubmit: (description: string, requirements: string) => void;
  isLoading: boolean;
}

export const SoftwareDescriptionForm: React.FC<SoftwareDescriptionFormProps> = ({
  onSubmit,
  isLoading,
}) => {
  const [description, setDescription] = useState('');
  const [requirements, setRequirements] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (description.trim()) {
      onSubmit(description, requirements);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Software Description *
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          rows={6}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Describe the software application you want to generate..."
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="requirements" className="block text-sm font-medium text-gray-700 mb-2">
          Requirements (Optional)
        </label>
        <textarea
          id="requirements"
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Add any specific requirements, constraints, or preferences..."
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || !description.trim()}
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Generating...' : 'Generate Software'}
      </button>
    </form>
  );
};


