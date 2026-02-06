import { useState, useEffect } from 'react';
import api from '../services/api';

const CHECKS = [
  { id: 'api', label: 'Conectando ao servidor', endpoint: '/health' },
  { id: 'database', label: 'Verificando banco de dados', endpoint: '/vagas/?limit=1' },
  { id: 'stats', label: 'Carregando estatísticas', endpoint: '/stats/' },
];

export default function LoadingScreen({ onComplete, onError }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState(CHECKS.map(() => 'pending')); // pending, loading, success, error
  const [error, setError] = useState(null);

  useEffect(() => {
    runHealthChecks();
  }, []);

  const runHealthChecks = async () => {
    const newStatus = [...status];

    for (let i = 0; i < CHECKS.length; i++) {
      setCurrentStep(i);
      newStatus[i] = 'loading';
      setStatus([...newStatus]);

      try {
        await api.get(CHECKS[i].endpoint);
        newStatus[i] = 'success';
        setStatus([...newStatus]);
        // Pequeno delay para feedback visual
        await new Promise(r => setTimeout(r, 300));
      } catch (err) {
        newStatus[i] = 'error';
        setStatus([...newStatus]);

        const errorInfo = {
          step: CHECKS[i].id,
          label: CHECKS[i].label,
          endpoint: CHECKS[i].endpoint,
          message: err.response?.data?.detail || err.message,
          status: err.response?.status,
          suggestion: getSuggestion(CHECKS[i].id, err),
        };

        setError(errorInfo);
        onError?.(errorInfo);
        return;
      }
    }

    // Todos os checks passaram
    await new Promise(r => setTimeout(r, 500));
    onComplete?.();
  };

  const getSuggestion = (checkId, err) => {
    if (err.code === 'ERR_NETWORK') {
      return 'CORS_OR_NETWORK: Verificar se backend está rodando e CORS configurado para origem do frontend';
    }

    switch (checkId) {
      case 'api':
        if (err.response?.status === 502 || err.response?.status === 503) {
          return 'BACKEND_SLEEPING: Serviço pode estar dormindo no Render. Aguarde 30-50s e recarregue.';
        }
        return 'API_UNREACHABLE: Verificar URL da API e se o serviço está ativo no Render';
      case 'database':
        if (err.response?.status === 500) {
          return 'DATABASE_ERROR: Verificar DATABASE_URL no Render e se Neon está ativo';
        }
        return 'DATABASE_QUERY_FAILED: Verificar conexão com PostgreSQL';
      case 'stats':
        return 'STATS_ENDPOINT_ERROR: Verificar rota /api/stats/ no backend';
      default:
        return 'UNKNOWN_ERROR: ' + err.message;
    }
  };

  const retry = () => {
    setError(null);
    setStatus(CHECKS.map(() => 'pending'));
    setCurrentStep(0);
    runHealthChecks();
  };

  const getStatusIcon = (s) => {
    switch (s) {
      case 'pending':
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />;
      case 'loading':
        return (
          <div className="w-5 h-5 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
        );
      case 'success':
        return (
          <div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center">
            <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo/Título */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 mb-4 shadow-lg shadow-indigo-200">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Vagas UX Platform</h1>
          <p className="text-gray-500 mt-1">Iniciando aplicação...</p>
        </div>

        {/* Card de Status */}
        <div className="bg-white rounded-2xl shadow-xl shadow-gray-200/50 p-6">
          {/* Passos */}
          <div className="space-y-4">
            {CHECKS.map((check, i) => (
              <div
                key={check.id}
                className={`flex items-center gap-4 p-3 rounded-xl transition-all duration-300 ${
                  status[i] === 'loading' ? 'bg-indigo-50' :
                  status[i] === 'error' ? 'bg-red-50' :
                  status[i] === 'success' ? 'bg-green-50' : 'bg-gray-50'
                }`}
              >
                {getStatusIcon(status[i])}
                <span className={`flex-1 text-sm font-medium ${
                  status[i] === 'loading' ? 'text-indigo-700' :
                  status[i] === 'error' ? 'text-red-700' :
                  status[i] === 'success' ? 'text-green-700' : 'text-gray-500'
                }`}>
                  {check.label}
                </span>
              </div>
            ))}
          </div>

          {/* Barra de Progresso */}
          {!error && (
            <div className="mt-6">
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 ease-out"
                  style={{
                    width: `${((status.filter(s => s === 'success').length) / CHECKS.length) * 100}%`
                  }}
                />
              </div>
            </div>
          )}

          {/* Erro */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 rounded-xl border border-red-100">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center">
                  <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-red-800">Falha: {error.label}</p>
                  <p className="text-xs text-red-600 mt-1 break-words">{error.message}</p>
                  <div className="mt-3 p-2 bg-red-100/50 rounded-lg">
                    <p className="text-xs font-mono text-red-700 break-all">{error.suggestion}</p>
                  </div>
                </div>
              </div>

              <button
                onClick={retry}
                className="mt-4 w-full py-2.5 px-4 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Tentar novamente
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-400 mt-6">
          Verificando conexões...
        </p>
      </div>
    </div>
  );
}
