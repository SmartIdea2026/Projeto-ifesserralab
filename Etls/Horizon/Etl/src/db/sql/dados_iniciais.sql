-- Valores iniciais dos tipos (decisão 8 da Etapa 1).
-- Categorias de produção do Lattes além de 'artigo' entram sob demanda, durante a carga.
INSERT INTO tipos_iniciativa (nome) VALUES
    ('projeto_pesquisa'),
    ('projeto_extensao'),
    ('projeto_desenvolvimento'),
    ('orientacao');

INSERT INTO tipos_producao (nome) VALUES
    ('artigo');
