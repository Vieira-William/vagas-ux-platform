export default function Filtros({ filtros, setFiltros }) {
  const handleChange = (campo, valor) => {
    setFiltros((prev) => ({
      ...prev,
      [campo]: valor || undefined,
    }));
  };

  const limparFiltros = () => {
    setFiltros({});
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-semibold text-gray-900">Filtros</h2>
        <button
          onClick={limparFiltros}
          className="text-xs text-blue-600 hover:text-blue-800"
        >
          Limpar
        </button>
      </div>

      <div className="space-y-4">
        {/* Fonte */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Fonte</label>
          <select
            value={filtros.fonte || ''}
            onChange={(e) => handleChange('fonte', e.target.value)}
            className="w-full text-sm border rounded px-3 py-2"
          >
            <option value="">Todas</option>
            <option value="indeed">Indeed</option>
            <option value="linkedin_jobs">LinkedIn Vagas</option>
            <option value="linkedin_posts">LinkedIn Posts</option>
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Status</label>
          <select
            value={filtros.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            className="w-full text-sm border rounded px-3 py-2"
          >
            <option value="">Todos</option>
            <option value="pendente">Pendente</option>
            <option value="aplicada">Aplicada</option>
            <option value="descartada">Descartada</option>
          </select>
        </div>

        {/* Modalidade */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Modalidade</label>
          <select
            value={filtros.modalidade || ''}
            onChange={(e) => handleChange('modalidade', e.target.value)}
            className="w-full text-sm border rounded px-3 py-2"
          >
            <option value="">Todas</option>
            <option value="remoto">Remoto</option>
            <option value="hibrido">Híbrido</option>
            <option value="presencial">Presencial</option>
          </select>
        </div>

        {/* Inglês */}
        <div>
          <label className="block text-sm text-gray-600 mb-1">Inglês</label>
          <select
            value={filtros.requisito_ingles || ''}
            onChange={(e) => handleChange('requisito_ingles', e.target.value)}
            className="w-full text-sm border rounded px-3 py-2"
          >
            <option value="">Todos</option>
            <option value="nenhum">Nenhum</option>
            <option value="basico">Básico</option>
            <option value="intermediario">Intermediário</option>
            <option value="fluente">Fluente</option>
          </select>
        </div>
      </div>
    </div>
  );
}
