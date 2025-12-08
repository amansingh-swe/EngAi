/**
 * Aman singh(67401334)
 * Sanmith Kurian (22256557)
 * Yash Agarwal (35564877)
 * Swapnil Nagras (26761683)
 * 
 * Main page for the EngAi application.
 */
import React, { useState } from 'react';
import Head from 'next/head';
import { SoftwareDescriptionForm } from '../components/SoftwareDescriptionForm';
import { CodeDisplay } from '../components/CodeDisplay';
import { TestDisplay } from '../components/TestDisplay';
import { UsageStatsComponent } from '../components/UsageStats';
import { api, SoftwareResponse } from '../api/client';

export default function Home() {
  const [result, setResult] = useState<SoftwareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (description: string, requirements: string) => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const response = await api.generateSoftware({
        description,
        requirements,
      });

      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate software. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>EngAi - Multi-Agent Code Generation</title>
        <meta name="description" content="Generate complete software applications using AI agents" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <header className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              EngAi
            </h1>
            <p className="text-lg text-gray-600">
              Multi-Agent System for Automated Software Generation
            </p>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Input Form */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-md p-6 sticky top-4">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                  Software Description
                </h2>
                <SoftwareDescriptionForm onSubmit={handleGenerate} isLoading={loading} />

                {error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-2 space-y-6">
              {loading && (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                  <p className="mt-4 text-gray-600">Generating your software...</p>
                  <p className="text-sm text-gray-500 mt-2">
                    This may take a minute. Our AI agents are working hard!
                  </p>
                </div>
              )}

              {result && (
                <>
                  <CodeDisplay title="Generated Architecture" code={result.architecture} />
                  <CodeDisplay title="Generated Code" code={result.code} />
                  <TestDisplay tests={result.tests} />
                </>
              )}

              {!loading && !result && (
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                  <p className="text-gray-500">
                    Enter a software description above to get started.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Usage Statistics */}
          <div className="mt-8">
            <UsageStatsComponent />
          </div>
        </div>
      </main>
    </>
  );
}


