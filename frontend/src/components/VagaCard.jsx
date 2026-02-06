import { vagasService } from '../services/api';

const statusColors = {
  pendente: 'bg-yellow-100 text-yellow-800',
  aplicada: 'bg-green-100 text-green-800',
  descartada: 'bg-gray-100 text-gray-800',
};

const fonteLabels = {
  indeed: 'Indeed',
  linkedin_jobs: 'LinkedIn Vagas',
  linkedin_posts: 'LinkedIn Posts',
};

export default function VagaCard({ vaga, onStatusChange }) {
  const handleStatusChange = async (novoStatus) => {
    try {
      await vagasService.atualizarStatus(vaga.id, novoStatus);
      onStatusChange();
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
      {/* Badges */}
      <div className="flex gap-2 mb-2 flex-wrap">
        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
          {fonteLabels[vaga.fonte] || vaga.fonte}
        </span>
        {vaga.tipo_vaga && (
          <span className="text-xs px-2 py-1 bg-purple-100 text-purple-800 rounded">
            {vaga.tipo_vaga}
          </span>
        )}
        {vaga.modalidade && vaga.modalidade !== 'nao_especificado' && (
          <span className="text-xs px-2 py-1 bg-teal-100 text-teal-800 rounded">
            {vaga.modalidade}
          </span>
        )}
      </div>

      {/* Título */}
      <h3 className="font-semibold text-gray-900 mb-1">{vaga.titulo}</h3>

      {/* Empresa e Local */}
      <p className="text-sm text-gray-600 mb-3">
        {vaga.empresa && <span>{vaga.empresa}</span>}
        {vaga.empresa && vaga.localizacao && <span> • </span>}
        {vaga.localizacao && <span>{vaga.localizacao}</span>}
      </p>

      {/* Inglês */}
      {vaga.requisito_ingles && vaga.requisito_ingles !== 'nao_especificado' && (
        <p className="text-xs text-gray-500 mb-3">
          Inglês: {vaga.requisito_ingles}
        </p>
      )}

      {/* Autor (para LinkedIn Posts) */}
      {vaga.nome_autor && vaga.fonte === 'linkedin_posts' && (
        <p className="text-xs text-gray-500 mb-3">
          Postado por: <span className="font-medium text-gray-700">{vaga.nome_autor}</span>
        </p>
      )}

      {/* Ações */}
      <div className="flex items-center justify-between pt-3 border-t">
        <div className="flex gap-2 flex-wrap">
          {vaga.link_vaga && (
            <a
              href={vaga.link_vaga}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 font-medium"
            >
              Ver vaga
            </a>
          )}
          {vaga.email_contato && (
            <a
              href={`mailto:${vaga.email_contato}?subject=Candidatura: ${vaga.titulo}`}
              className="text-xs px-3 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 font-medium"
            >
              Enviar Email
            </a>
          )}
          {vaga.perfil_autor && (
            <a
              href={vaga.perfil_autor}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 font-medium"
            >
              Contatar Autor
            </a>
          )}
          {/* Fallback: buscar no LinkedIn quando não tem link/email/perfil */}
          {!vaga.link_vaga && !vaga.email_contato && !vaga.perfil_autor && vaga.nome_autor && (
            <a
              href={`https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(vaga.nome_autor)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 font-medium"
            >
              Buscar Autor
            </a>
          )}
          {/* Fallback final: buscar vaga no LinkedIn */}
          {!vaga.link_vaga && !vaga.email_contato && !vaga.perfil_autor && !vaga.nome_autor && (
            <a
              href={`https://www.linkedin.com/search/results/content/?keywords=${encodeURIComponent(vaga.titulo)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              Buscar no LinkedIn
            </a>
          )}
        </div>

        {/* Status */}
        <select
          value={vaga.status}
          onChange={(e) => handleStatusChange(e.target.value)}
          className={`text-xs px-2 py-1 rounded border-0 cursor-pointer ${statusColors[vaga.status]}`}
        >
          <option value="pendente">Pendente</option>
          <option value="aplicada">Aplicada</option>
          <option value="descartada">Descartada</option>
        </select>
      </div>
    </div>
  );
}
