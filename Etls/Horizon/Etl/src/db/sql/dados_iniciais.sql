-- Valores iniciais dos tipos (decisão 8 da Etapa 1).
-- Categorias de produção do Lattes além de 'artigo' entram sob demanda, durante a carga.
INSERT INTO tipos_iniciativa (nome) VALUES
    ('projeto_pesquisa'),
    ('projeto_extensao'),
    ('projeto_desenvolvimento'),
    ('orientacao');

INSERT INTO tipos_producao (nome) VALUES
    ('artigo');

-- IFES: organização-mãe dos campi (unidades). Um registro só, com o nome por extenso.
INSERT INTO organizacoes (nome, sigla, tipo) VALUES
    ('Instituto Federal do Espírito Santo', 'IFES', 'instituicao_ensino');

-- Papéis fixos de participação em iniciativa e de membro de equipe.
-- Papéis de vínculo vêm do campo 'vinculo' do Lattes e são criados durante a carga.
-- Mantenha em sincronia com PAPEIS_FIXOS em src/core/ports/repositorio_organizacoes.py.
INSERT INTO papeis (nome, escopo) VALUES
    ('coordenador', 'participacao'),
    ('pesquisador', 'participacao'),
    ('estudante', 'participacao'),
    ('orientador', 'participacao'),
    ('orientando', 'participacao'),
    ('lider', 'equipe'),
    ('pesquisador', 'equipe'),
    ('estudante', 'equipe'),
    ('tecnico', 'equipe');
