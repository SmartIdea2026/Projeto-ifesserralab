"""Lógica de persistência no banco de dados e UPSERTs - Normalizado."""

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import re
import unicodedata
from . import models, database

def get_or_create_lookup(db: Session, model_class, nome: str) -> int:
    """Busca ou cria um registro em tabelas de domínio (lookups)."""
    if not nome or not nome.strip():
        return None
    nome = nome.strip()
    obj = db.query(model_class).filter(model_class.nome == nome).first()
    if not obj:
        obj = model_class(nome=nome)
        db.add(obj)
        db.commit()
        db.refresh(obj)
    return obj.id


def get_or_create_pessoa(db: Session, nome: str, cpf: str = None, email: str = None, vinculo: str = None) -> int:
    """Retorna o ID da pessoa, criando ou atualizando conforme as chaves únicas."""
    if not nome or nome.strip() == "":
        nome = "Desconhecido"
    else:
        # A fonte traz o nome. Usamos diretamente o que vem da fonte.
        nome = nome.strip()
        
    # Tenta achar por CPF
    if cpf and cpf.strip() != "":
        pessoa = db.query(database.Pessoa).filter(database.Pessoa.cpf == cpf).first()
        if pessoa:
            updated = False
            if email and not pessoa.email:
                pessoa.email = email
                updated = True
            if pessoa.nome == "Desconhecido" and nome != "Desconhecido":
                pessoa.nome = nome
                updated = True
            if not pessoa.vinculo and vinculo:
                pessoa.vinculo = vinculo
                updated = True
            if updated:
                db.commit()
            return pessoa.id
            
    # Tenta achar por Email
    if email and email.strip() != "":
        pessoa = db.query(database.Pessoa).filter(database.Pessoa.email == email).first()
        if pessoa:
            updated = False
            if cpf and not pessoa.cpf:
                pessoa.cpf = cpf
                updated = True
            if pessoa.nome == "Desconhecido" and nome != "Desconhecido":
                pessoa.nome = nome
                updated = True
            if not pessoa.vinculo and vinculo:
                pessoa.vinculo = vinculo
                updated = True
            if updated:
                db.commit()
            return pessoa.id
            
    # Tenta achar por Nome Exato (fallback para evitar duplicação se o CPF ou Email não veio)
    if nome != "Desconhecido":
        pessoa = db.query(database.Pessoa).filter(database.Pessoa.nome == nome).first()
        if pessoa:
            # Se a pessoa no banco JÁ TEM um CPF diferente do que estamos inserindo,
            # então é um homônimo exato! Vamos forçar a criação de um novo registro.
            if pessoa.cpf and cpf and pessoa.cpf != cpf:
                pass # Cai fora do bloco if e vai criar nova pessoa abaixo
            else:
                updated = False
                if cpf and not pessoa.cpf:
                    pessoa.cpf = cpf
                    updated = True
                if email and not pessoa.email:
                    pessoa.email = email
                    updated = True
                if not pessoa.vinculo and vinculo:
                    pessoa.vinculo = vinculo
                    updated = True
                if updated:
                    db.commit()
                return pessoa.id
            
    # Cria nova pessoa
    nova_pessoa = database.Pessoa(
        nome=nome, 
        cpf=cpf if cpf else None, 
        email=email if email else None,
        vinculo=vinculo
    )
    db.add(nova_pessoa)
    db.commit()
    db.refresh(nova_pessoa)
    return nova_pessoa.id


def upsert_acao(db: Session, acao_pydantic: models.Acao):
    """Insere ou atualiza uma Ação (Projeto/Curso/Evento) resolvendo lookups."""
    import datetime
    # Agora a unicidade é garantida pelo acao_original_id

    # Resolve Lookups
    fk_tipo_id = get_or_create_lookup(db, database.TipoAcao, acao_pydantic.tipo)
    fk_fomento_id = get_or_create_lookup(db, database.Fomento, acao_pydantic.fomento)
    fk_campus_id = get_or_create_lookup(db, database.Campus, acao_pydantic.campus)
    fk_natureza_id = get_or_create_lookup(db, database.Natureza, acao_pydantic.natureza)
    
    # Coordenador
    fk_coord_id = None
    if acao_pydantic.coordenador:
        fk_coord_id = get_or_create_pessoa(db, nome=acao_pydantic.coordenador)
        
    relat_aprovado = None
    if acao_pydantic.relatorio_aprovado:
        relat_aprovado = (acao_pydantic.relatorio_aprovado.lower() == 'sim')
        
    data_cadastro_date = None
    if acao_pydantic.data_cadastro:
        try:
            # Assuming format DD/MM/YYYY
            data_cadastro_date = datetime.datetime.strptime(acao_pydantic.data_cadastro, "%d/%m/%Y").date()
        except ValueError:
            data_cadastro_date = None
            
    stmt = insert(database.Acao).values(
        acao_original_id=acao_pydantic.acao_id,
        processo=acao_pydantic.processo,
        titulo=acao_pydantic.titulo,
        data_cadastro=data_cadastro_date,
        relatorio_aprovado=relat_aprovado,
        url_detalhe=acao_pydantic.url_detalhe,
        fk_TipoAcao_id=fk_tipo_id,
        fk_Coordenador_id=fk_coord_id,
        fk_Natureza_id=fk_natureza_id
    )
    
    stmt = stmt.on_conflict_do_update(
        index_elements=['acao_original_id'],
        set_={
            'titulo': stmt.excluded.titulo,
            'relatorio_aprovado': stmt.excluded.relatorio_aprovado,
            'data_cadastro': stmt.excluded.data_cadastro,
            'fk_TipoAcao_id': stmt.excluded.fk_TipoAcao_id,
            'fk_Coordenador_id': stmt.excluded.fk_Coordenador_id,
            'fk_Natureza_id': stmt.excluded.fk_Natureza_id
        }
    )
    db.execute(stmt)
    db.commit()
    
    # Associações M:N
    acao_db = db.query(database.Acao).filter(database.Acao.acao_original_id == acao_pydantic.acao_id).first()
    if acao_db:
        if fk_fomento_id:
            existe_fomento = db.query(database.FinanciamentoAcao).filter(
                database.FinanciamentoAcao.fk_Fomento_id == fk_fomento_id, 
                database.FinanciamentoAcao.fk_Acao_id == acao_db.id
            ).first()
            if not existe_fomento:
                db.add(database.FinanciamentoAcao(fk_Fomento_id=fk_fomento_id, fk_Acao_id=acao_db.id))
        
        if fk_campus_id:
            existe_campus = db.query(database.LocalAcao).filter(
                database.LocalAcao.fk_Campus_id == fk_campus_id, 
                database.LocalAcao.fk_Acao_id == acao_db.id
            ).first()
            if not existe_campus:
                db.add(database.LocalAcao(fk_Campus_id=fk_campus_id, fk_Acao_id=acao_db.id))
                
        db.commit()

def upsert_participacoes(db: Session, part: models.AcaoParticipacoes):
    """Insere atividades, público-alvo e equipe associados a uma ação."""
    acao = db.query(database.Acao).filter(database.Acao.processo == part.processo).first()
    if not acao:
        return 
        
    for ativ in part.atividades:
        if not ativ.atividade_id:
            continue
            
        fk_tipo_ativ_id = get_or_create_lookup(db, database.TipoAtividade, ativ.tipo)
            
        # 1. Atividade (UPSERT)
        stmt_ativ = insert(database.Atividade).values(
            atividade_original_id=ativ.atividade_id,
            fk_Acao_id=acao.id,
            nome=ativ.atividade,
            fk_TipoAtividade_id=fk_tipo_ativ_id
        )
        stmt_ativ = stmt_ativ.on_conflict_do_update(
            index_elements=['atividade_original_id'],
            set_={
                'nome': stmt_ativ.excluded.nome,
                'fk_TipoAtividade_id': stmt_ativ.excluded.fk_TipoAtividade_id
            }
        )
        res = db.execute(stmt_ativ)
        db.commit()
        
        # Recupera o ID interno da Atividade recém inserida ou atualizada
        atividade_obj = db.query(database.Atividade).filter(database.Atividade.atividade_original_id == ativ.atividade_id).first()
        if not atividade_obj:
            continue
        ativ_id_db = atividade_obj.id
        
        # 2. Equipe Executora
        for membro in ativ.equipe_execucao:
            nome = membro.get("Nome", "Desconhecido")
            cpf = membro.get("CPF")
            email = membro.get("E-mail")
            vinculo = membro.get("Vínculo")
            pessoa_id = get_or_create_pessoa(db, nome, cpf, email, vinculo=vinculo)
            
            fk_funcao_id = get_or_create_lookup(db, database.Funcao, membro.get("Função"))
            
            existe = db.query(database.EquipeExecucao).filter(
                database.EquipeExecucao.fk_Atividade_id == ativ_id_db,
                database.EquipeExecucao.fk_Pessoa_id == pessoa_id
            ).first()
            
            if not existe:
                pe = database.EquipeExecucao(
                    fk_Atividade_id=ativ_id_db,
                    fk_Pessoa_id=pessoa_id,
                    fk_Funcao_id=fk_funcao_id
                )
                db.add(pe)
                db.commit()

        # 3. Público-Alvo
        for aluno in ativ.publico_alvo:
            nome = aluno.get("Nome", "Desconhecido")
            cpf = aluno.get("CPF")
            email = aluno.get("E-mail")
            pessoa_id = get_or_create_pessoa(db, nome, cpf, email)
            
            carga_str = str(aluno.get("Carga horária", "0"))
            try:
                carga = float(carga_str.replace("h", "").replace(",", ".").strip())
            except ValueError:
                carga = 0.0
                
            certificado_str = str(aluno.get("Certificado", "Não"))
            certificado = True if "sim" in certificado_str.lower() else False
            
            existe = db.query(database.PublicoAlvo).filter(
                database.PublicoAlvo.fk_Atividade_id == ativ_id_db,
                database.PublicoAlvo.fk_Pessoa_id == pessoa_id
            ).first()
            
            if not existe:
                pp = database.PublicoAlvo(
                    fk_Atividade_id=ativ_id_db,
                    fk_Pessoa_id=pessoa_id,
                    situacao=aluno.get("Situação"),
                    carga_horaria=carga,
                    certificado=certificado
                )
                db.add(pp)
                db.commit()
