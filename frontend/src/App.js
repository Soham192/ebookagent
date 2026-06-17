import { useEffect, useState } from 'react';
import UploadForm from './components/UploadForm';

function App() {
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.localStorage.getItem('theme') === 'dark';
    }
    return false;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add('dark');
      window.localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      window.localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6 dark:bg-slate-950 dark:text-slate-100">
      <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 dark:bg-slate-900">
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold">Kindle Agent</h1>
            <p className="text-slate-600 dark:text-slate-300">Upload a PDF and get a Kindle-ready ebook.</p>
          </div>
          <button
            type="button"
            onClick={() => setDarkMode((value) => !value)}
            className="rounded-full border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-900 shadow-sm transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
          >
            {darkMode ? 'Light mode' : 'Dark mode'}
          </button>
        </div>

        <UploadForm onResult={setResult} />

        {result && (
          <div className="mt-6 p-4 border rounded-lg bg-slate-50 dark:bg-slate-800 dark:border-slate-700">
            <h2 className="text-xl font-semibold mb-2">Conversion Complete</h2>
            <div className="text-sm text-slate-700 dark:text-slate-200 space-y-2">
              <p><strong>Title:</strong> {result.output?.title || 'Unknown Title'}</p>
              <p><strong>Author:</strong> {result.output?.author || 'Unknown Author'}</p>
              <p><strong>Format:</strong> {result.output?.format?.toUpperCase() || 'AZW3'}</p>
              <p><strong>OCR required:</strong> {result.output?.requires_ocr ? 'Yes' : 'No'}</p>
              {result.kindle_delivery && (
                <div>
                  <p>
                    <strong>Kindle delivery:</strong>{' '}
                    {result.kindle_delivery.sent ? `sent to ${result.kindle_delivery.recipient}` : 'failed'}
                  </p>
                  {!result.kindle_delivery.sent && result.kindle_delivery.error && (
                    <p className="text-xs text-red-400">{result.kindle_delivery.error}</p>
                  )}
                </div>
              )}
            </div>
            {result.status === 'ok' && result.download_url && (
              <div className="mt-4">
                <a
                  href={result.download_url}
                  className="inline-flex items-center justify-center rounded-full bg-slate-900 text-white px-5 py-3 text-sm font-semibold hover:bg-slate-700 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200"
                >
                  Download {result.output?.format?.toUpperCase() || 'AZW3'}
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
