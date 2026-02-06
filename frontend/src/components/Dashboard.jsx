import { useState, useEffect } from 'react';
import { vagasService, statsService, scraperService } from '../services/api';
import VagaCard from './VagaCard';
import Filtros from './Filtros';

export default function Dashboard() {
  const [vagas, setVagas] = useState([]);
  const [stats, setStats] = useState(null);
  const [filtros, setFiltros] = useState({});
  const [loading, setLoading] = useState(true);
  const [coletando, setColetando] = useState(false);
  const [mensagem, setMensagem] = useState(null);

  const carregarVagas = async () => {
    try {
      setLoading(true);
      const [vagasRes, statsRes] = await Promise.all([
        vagasService.listar(filtros),
        statsService.obter(),
      ]);
      setVagas(vagasRes.data.vagas);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Erro ao carregar vagas:', error);
    } finally {
      setLoading(false);
    }
  };

  const coletarVagas = async () => {
    try {
      setColetando(true);
      setMensagem({ tipo: 'info', texto: 'Coletando vagas... Isso pode levar alguns minutos.' });
      const res = await scraperService.coletarTudo();
      const novas = res.data.total_novas || 0;
      setMensagem({
        tipo: 'sucesso',
        texto: novas > 0 ? `${novas} novas vagas encontradas!` : 'Nenhuma vaga nova encontrada.'
      });
      carregarVagas();
    } catch (error) {
      setMensagem({ tipo: 'erro', texto: 'Erro ao coletar vagas.' });
    } finally {
      setColetando(false);
      setTimeout(() => setMensagem(null), 5000);
    }
  };

  useEffect(() => {
    carregarVagas();
  }, [filtros]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-900">Vagas UX</h1>
          <button
            onClick={coletarVagas}
            disabled={coletando}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              coletando
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {coletando ? 'Coletando...' : 'Coletar Vagas'}
          </button>
        </div>
      </header>

      {/* Mensagem */}
      {mensagem && (
        <div className={`max-w-7xl mx-auto px-4 mt-4`}>
          <div className={`p-3 rounded-lg ${
            mensagem.tipo === 'sucesso' ? 'bg-green-100 text-green-800' :
            mensagem.tipo === 'erro' ? 'bg-red-100 text-red-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {mensagem.texto}
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-2xl font-bold text-gray-900">{stats.total_vagas}</p>
              <p className="text-sm text-gray-500">Total</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-2xl font-bold text-yellow-600">{stats.por_status?.pendente || 0}</p>
              <p className="text-sm text-gray-500">Pendentes</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-2xl font-bold text-green-600">{stats.por_status?.aplicada || 0}</p>
              <p className="text-sm text-gray-500">Aplicadas</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <p className="text-2xl font-bold text-blue-600">{stats.ultimas_24h}</p>
              <p className="text-sm text-gray-500">Últimas 24h</p>
            </div>
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-6">
          {/* Filtros - Sidebar */}
          <aside className="w-full md:w-64 flex-shrink-0">
            <Filtros filtros={filtros} setFiltros={setFiltros} />
          </aside>

          {/* Lista de Vagas */}
          <section className="flex-1">
            {loading ? (
              <div className="text-center py-12">
                <p className="text-gray-500">Carregando...</p>
              </div>
            ) : vagas.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-500">Nenhuma vaga encontrada</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {vagas.map((vaga) => (
                  <VagaCard
                    key={vaga.id}
                    vaga={vaga}
                    onStatusChange={carregarVagas}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
