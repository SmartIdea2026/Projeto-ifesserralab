
CREATE TABLE pessoas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL
);

CREATE TABLE emails_pessoa (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE identificadores_pessoa (
    pessoa_id INTEGER,
    fonte VARCHAR(30) CHECK (fonte IN ('lattes', 'sigpesq', 'extensao', 'egressos')),
    codigo VARCHAR(255) NOT NULL,
    PRIMARY KEY (pessoa_id, fonte)
);

CREATE TABLE perfis_lattes (
    pessoa_id INTEGER PRIMARY KEY,
    resumo TEXT NOT NULL,
    nomes_citacao VARCHAR(255) NOT NULL,
    atualizado_em DATETIME NOT NULL
);

CREATE TABLE formacoes_academicas (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER NOT NULL,
    tipo_formacao_id INTEGER NOT NULL,
    organizacao_id INTEGER NOT NULL,
    curso VARCHAR(255) NOT NULL,
    ano_inicio INTEGER NOT NULL,
    ano_fim INTEGER,
    titulo_tese VARCHAR(255)
);

CREATE TABLE orientadores_formacao (
    formacao_id INTEGER,
    pessoa_id INTEGER,
    papel VARCHAR(30) NOT NULL CHECK (papel IN ('orientador', 'coorientador')),
    PRIMARY KEY (formacao_id, pessoa_id)
);

CREATE TABLE premios (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    ano INTEGER
);

CREATE TABLE proficiencias (
    pessoa_id INTEGER,
    idioma_id INTEGER,
    leitura VARCHAR(255) NOT NULL,
    escrita VARCHAR(255) NOT NULL,
    fala VARCHAR(255) NOT NULL,
    compreensao VARCHAR(255) NOT NULL,
    PRIMARY KEY (pessoa_id, idioma_id)
);

CREATE TABLE idiomas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE tipos_formacao (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE organizacoes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sigla VARCHAR(255),
    tipo VARCHAR(30) NOT NULL CHECK (tipo IN ('instituicao_ensino', 'fomento', 'empresa', 'orgao_publico', 'unidade'))
);

CREATE TABLE unidades_organizacionais (
    id INTEGER PRIMARY KEY,
    organizacao_pai_id INTEGER NOT NULL
);

CREATE TABLE vinculos (
    id INTEGER PRIMARY KEY,
    pessoa_id INTEGER NOT NULL,
    organizacao_id INTEGER NOT NULL,
    papel_id INTEGER NOT NULL,
    data_inicio DATE,
    data_fim DATE
);

CREATE TABLE papeis (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    escopo VARCHAR(30) NOT NULL CHECK (escopo IN ('vinculo', 'equipe', 'participacao'))
);

CREATE TABLE equipes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sigla VARCHAR(255),
    descricao TEXT,
    organizacao_id INTEGER NOT NULL
);

CREATE TABLE grupos_pesquisa (
    id INTEGER PRIMARY KEY,
    url_cnpq VARCHAR(255) UNIQUE,
    data_inicio DATE
);

CREATE TABLE membros_equipe (
    id INTEGER PRIMARY KEY,
    equipe_id INTEGER NOT NULL,
    pessoa_id INTEGER NOT NULL,
    papel_id INTEGER NOT NULL,
    data_inicio DATE,
    data_fim DATE
);

CREATE TABLE areas_conhecimento_equipe (
    equipe_id INTEGER,
    area_id INTEGER,
    PRIMARY KEY (equipe_id, area_id)
);

CREATE TABLE iniciativas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo_iniciativa_id INTEGER NOT NULL,
    organizacao_id INTEGER NOT NULL,
    situacao VARCHAR(255) NOT NULL,
    descricao TEXT,
    data_inicio DATE,
    data_fim DATE
);

CREATE TABLE tipos_iniciativa (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE hierarquia_iniciativas (
    iniciativa_id INTEGER PRIMARY KEY,
    iniciativa_pai_id INTEGER NOT NULL
);

CREATE TABLE participantes_iniciativa (
    id INTEGER PRIMARY KEY,
    iniciativa_id INTEGER NOT NULL,
    pessoa_id INTEGER NOT NULL,
    papel_id INTEGER NOT NULL,
    data_inicio DATE,
    data_fim DATE
);

CREATE TABLE bolsas_participante (
    participante_id INTEGER PRIMARY KEY,
    bolsa_id INTEGER NOT NULL
);

CREATE TABLE bolsas (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    valor DECIMAL(10,2) NOT NULL,
    financiador_id INTEGER NOT NULL
);

CREATE TABLE equipes_iniciativa (
    iniciativa_id INTEGER,
    equipe_id INTEGER,
    papel VARCHAR(30) NOT NULL CHECK (papel IN ('executor', 'parceiro')),
    PRIMARY KEY (iniciativa_id, equipe_id)
);

CREATE TABLE organizacoes_iniciativa (
    iniciativa_id INTEGER,
    organizacao_id INTEGER,
    papel VARCHAR(30) CHECK (papel IN ('demandante', 'financiadora', 'parceira')),
    PRIMARY KEY (iniciativa_id, organizacao_id, papel)
);

CREATE TABLE areas_conhecimento_iniciativa (
    iniciativa_id INTEGER,
    area_id INTEGER,
    PRIMARY KEY (iniciativa_id, area_id)
);

CREATE TABLE producoes (
    id INTEGER PRIMARY KEY,
    tipo_producao_id INTEGER NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    ano INTEGER NOT NULL,
    link VARCHAR(255)
);

CREATE TABLE artigos (
    id INTEGER PRIMARY KEY,
    veiculo VARCHAR(255) NOT NULL,
    volume VARCHAR(255),
    paginas VARCHAR(255),
    doi VARCHAR(255) UNIQUE
);

CREATE TABLE autores_producao (
    producao_id INTEGER,
    pessoa_id INTEGER,
    PRIMARY KEY (producao_id, pessoa_id)
);

CREATE TABLE tipos_producao (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE areas_conhecimento (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE areas_conhecimento_pessoa (
    pessoa_id INTEGER,
    area_id INTEGER,
    PRIMARY KEY (pessoa_id, area_id)
);
 
ALTER TABLE emails_pessoa ADD CONSTRAINT FK_emails_pessoa_3
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE identificadores_pessoa ADD CONSTRAINT FK_identificadores_pessoa_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE perfis_lattes ADD CONSTRAINT FK_perfis_lattes_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE formacoes_academicas ADD CONSTRAINT FK_formacoes_academicas_2
    FOREIGN KEY (tipo_formacao_id)
    REFERENCES tipos_formacao (id);
 
ALTER TABLE formacoes_academicas ADD CONSTRAINT FK_formacoes_academicas_3
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE formacoes_academicas ADD CONSTRAINT FK_formacoes_academicas_4
    FOREIGN KEY (organizacao_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE orientadores_formacao ADD CONSTRAINT FK_orientadores_formacao_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE orientadores_formacao ADD CONSTRAINT FK_orientadores_formacao_3
    FOREIGN KEY (formacao_id)
    REFERENCES formacoes_academicas (id);
 
ALTER TABLE premios ADD CONSTRAINT FK_premios_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE proficiencias ADD CONSTRAINT FK_proficiencias_2
    FOREIGN KEY (idioma_id)
    REFERENCES idiomas (id);
 
ALTER TABLE proficiencias ADD CONSTRAINT FK_proficiencias_3
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE unidades_organizacionais ADD CONSTRAINT FK_unidades_organizacionais_2
    FOREIGN KEY (id)
    REFERENCES organizacoes (id);
 
ALTER TABLE unidades_organizacionais ADD CONSTRAINT FK_unidades_organizacionais_3
    FOREIGN KEY (organizacao_pai_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE vinculos ADD CONSTRAINT FK_vinculos_2
    FOREIGN KEY (papel_id)
    REFERENCES papeis (id);
 
ALTER TABLE vinculos ADD CONSTRAINT FK_vinculos_3
    FOREIGN KEY (organizacao_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE vinculos ADD CONSTRAINT FK_vinculos_4
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE equipes ADD CONSTRAINT FK_equipes_2
    FOREIGN KEY (organizacao_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE grupos_pesquisa ADD CONSTRAINT FK_grupos_pesquisa_3
    FOREIGN KEY (id)
    REFERENCES equipes (id);
 
ALTER TABLE membros_equipe ADD CONSTRAINT FK_membros_equipe_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE membros_equipe ADD CONSTRAINT FK_membros_equipe_3
    FOREIGN KEY (papel_id)
    REFERENCES papeis (id);
 
ALTER TABLE membros_equipe ADD CONSTRAINT FK_membros_equipe_4
    FOREIGN KEY (equipe_id)
    REFERENCES equipes (id);
 
ALTER TABLE areas_conhecimento_equipe ADD CONSTRAINT FK_areas_conhecimento_equipe_2
    FOREIGN KEY (area_id)
    REFERENCES areas_conhecimento (id);
 
ALTER TABLE areas_conhecimento_equipe ADD CONSTRAINT FK_areas_conhecimento_equipe_3
    FOREIGN KEY (equipe_id)
    REFERENCES equipes (id);
 
ALTER TABLE iniciativas ADD CONSTRAINT FK_iniciativas_2
    FOREIGN KEY (tipo_iniciativa_id)
    REFERENCES tipos_iniciativa (id);
 
ALTER TABLE iniciativas ADD CONSTRAINT FK_iniciativas_3
    FOREIGN KEY (organizacao_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE hierarquia_iniciativas ADD CONSTRAINT FK_hierarquia_iniciativas_2
    FOREIGN KEY (iniciativa_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE hierarquia_iniciativas ADD CONSTRAINT FK_hierarquia_iniciativas_3
    FOREIGN KEY (iniciativa_pai_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE participantes_iniciativa ADD CONSTRAINT FK_participantes_iniciativa_2
    FOREIGN KEY (iniciativa_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE participantes_iniciativa ADD CONSTRAINT FK_participantes_iniciativa_3
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE participantes_iniciativa ADD CONSTRAINT FK_participantes_iniciativa_4
    FOREIGN KEY (papel_id)
    REFERENCES papeis (id);
 
ALTER TABLE bolsas_participante ADD CONSTRAINT FK_bolsas_participante_2
    FOREIGN KEY (participante_id)
    REFERENCES participantes_iniciativa (id);
 
ALTER TABLE bolsas_participante ADD CONSTRAINT FK_bolsas_participante_3
    FOREIGN KEY (bolsa_id)
    REFERENCES bolsas (id);
 
ALTER TABLE bolsas ADD CONSTRAINT FK_bolsas_3
    FOREIGN KEY (financiador_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE equipes_iniciativa ADD CONSTRAINT FK_equipes_iniciativa_2
    FOREIGN KEY (equipe_id)
    REFERENCES equipes (id);
 
ALTER TABLE equipes_iniciativa ADD CONSTRAINT FK_equipes_iniciativa_3
    FOREIGN KEY (iniciativa_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE organizacoes_iniciativa ADD CONSTRAINT FK_organizacoes_iniciativa_2
    FOREIGN KEY (organizacao_id)
    REFERENCES organizacoes (id);
 
ALTER TABLE organizacoes_iniciativa ADD CONSTRAINT FK_organizacoes_iniciativa_3
    FOREIGN KEY (iniciativa_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE areas_conhecimento_iniciativa ADD CONSTRAINT FK_areas_conhecimento_iniciativa_2
    FOREIGN KEY (iniciativa_id)
    REFERENCES iniciativas (id);
 
ALTER TABLE areas_conhecimento_iniciativa ADD CONSTRAINT FK_areas_conhecimento_iniciativa_3
    FOREIGN KEY (area_id)
    REFERENCES areas_conhecimento (id);
 
ALTER TABLE producoes ADD CONSTRAINT FK_producoes_2
    FOREIGN KEY (tipo_producao_id)
    REFERENCES tipos_producao (id);
 
ALTER TABLE artigos ADD CONSTRAINT FK_artigos_3
    FOREIGN KEY (id)
    REFERENCES producoes (id);
 
ALTER TABLE autores_producao ADD CONSTRAINT FK_autores_producao_2
    FOREIGN KEY (producao_id)
    REFERENCES producoes (id);
 
ALTER TABLE autores_producao ADD CONSTRAINT FK_autores_producao_3
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE areas_conhecimento_pessoa ADD CONSTRAINT FK_areas_conhecimento_pessoa_2
    FOREIGN KEY (pessoa_id)
    REFERENCES pessoas (id);
 
ALTER TABLE areas_conhecimento_pessoa ADD CONSTRAINT FK_areas_conhecimento_pessoa_3
    FOREIGN KEY (area_id)
    REFERENCES areas_conhecimento (id);
