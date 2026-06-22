"""
Popula o banco com notícias de demonstração baseadas em conteúdo real
do TSE e TREs. Útil para testes locais sem acesso à internet.
"""
from datetime import datetime, timedelta, timezone
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "news.db"

DEMO_NEWS = [
    # TSE
    {
        "sigla": "TSE",
        "nome": "Tribunal Superior Eleitoral",
        "title": "TSE aprova resolução sobre propaganda eleitoral antecipada",
        "summary": "O Tribunal Superior Eleitoral (TSE) aprovou nesta terça-feira resolução que regulamenta a propaganda eleitoral antecipada para as eleições municipais. A norma estabelece critérios para identificação de condutas vedadas e multas para infratores.",
        "url": "https://www.tse.jus.br/comunicacao/noticias/2024/resolucao-propaganda-eleitoral",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
    },
    {
        "sigla": "TSE",
        "nome": "Tribunal Superior Eleitoral",
        "title": "Presidente do TSE defende fortalecimento da democracia em discurso",
        "summary": "A presidenta do Tribunal Superior Eleitoral destacou a importância da participação popular no processo democrático e anunciou novas iniciativas de educação eleitoral para jovens eleitores.",
        "url": "https://www.tse.jus.br/comunicacao/noticias/2024/presidente-democracia",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
    },
    {
        "sigla": "TSE",
        "nome": "Tribunal Superior Eleitoral",
        "title": "TSE lança campanha de recadastramento biométrico em todo o país",
        "summary": "O TSE iniciou nesta segunda-feira a campanha nacional de recadastramento biométrico. Eleitores que não realizarem o procedimento até o prazo terão o título cancelado automaticamente.",
        "url": "https://www.tse.jus.br/comunicacao/noticias/2024/recadastramento-biometrico",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    },
    {
        "sigla": "TSE",
        "nome": "Tribunal Superior Eleitoral",
        "title": "Urnas eletrônicas passam por auditoria pública com participação de partidos",
        "summary": "O TSE realizou nova rodada de auditoria do sistema de votação eletrônica com participação de representantes de partidos políticos, Ministério Público, OAB e especialistas em segurança digital.",
        "url": "https://www.tse.jus.br/comunicacao/noticias/2024/auditoria-urnas",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    },
    {
        "sigla": "TSE",
        "nome": "Tribunal Superior Eleitoral",
        "title": "TSE publica dados abertos sobre financiamento de campanha eleitoral",
        "summary": "O portal de dados abertos do TSE disponibilizou novos conjuntos de dados sobre as prestações de contas das campanhas eleitorais, permitindo maior transparência e controle social.",
        "url": "https://www.tse.jus.br/comunicacao/noticias/2024/dados-abertos-financiamento",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
    },
    # TRE-SP
    {
        "sigla": "TRE-SP",
        "nome": "TRE de São Paulo",
        "title": "TRE-SP abre inscrições para programa de educação eleitoral nas escolas",
        "summary": "O Tribunal Regional Eleitoral de São Paulo abriu as inscrições para o programa Eleitor do Futuro, que leva educação eleitoral às escolas públicas e privadas do estado.",
        "url": "https://www.tre-sp.jus.br/comunicacao/noticias/2024/educacao-eleitoral-escolas",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
    },
    {
        "sigla": "TRE-SP",
        "nome": "TRE de São Paulo",
        "title": "Cartórios eleitorais de SP ampliam horário de atendimento",
        "summary": "Os cartórios eleitorais do estado de São Paulo ampliarão o horário de atendimento nos próximos meses para facilitar o acesso dos eleitores aos serviços de alistamento, transferência e revisão eleitoral.",
        "url": "https://www.tre-sp.jus.br/comunicacao/noticias/2024/horario-cartorios",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=1, hours=4)).isoformat(),
    },
    # TRE-RJ
    {
        "sigla": "TRE-RJ",
        "nome": "TRE do Rio de Janeiro",
        "title": "TRE-RJ cassa mandato de vereador por abuso de poder econômico",
        "summary": "O Tribunal Regional Eleitoral do Rio de Janeiro cassou o mandato de um vereador da capital fluminense por uso de recursos ilegais durante a campanha eleitoral, conforme decisão unânime do pleno.",
        "url": "https://www.tre-rj.jus.br/comunicacao/noticias/2024/cassa-mandato-vereador",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
    },
    {
        "sigla": "TRE-RJ",
        "nome": "TRE do Rio de Janeiro",
        "title": "TRE-RJ promove mutirão de atendimento na Baixada Fluminense",
        "summary": "O TRE-RJ realizará mutirão de atendimento ao eleitor nos municípios da Baixada Fluminense neste fim de semana, com serviços como emissão de título, transferência eleitoral e biometria.",
        "url": "https://www.tre-rj.jus.br/comunicacao/noticias/2024/mutirao-baixada",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    },
    # TRE-MG
    {
        "sigla": "TRE-MG",
        "nome": "TRE de Minas Gerais",
        "title": "TRE-MG capacita mesários para as eleições municipais",
        "summary": "O Tribunal Regional Eleitoral de Minas Gerais iniciou o programa de capacitação de mesários para as eleições municipais, com treinamento presencial e módulos online disponíveis na plataforma EAD.",
        "url": "https://www.tre-mg.jus.br/comunicacao/noticias/2024/capacitacao-mesarios",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
    },
    # TRE-RS
    {
        "sigla": "TRE-RS",
        "nome": "TRE do Rio Grande do Sul",
        "title": "TRE-RS reconstrói seção eleitoral após enchentes históricas",
        "summary": "O Tribunal Regional Eleitoral do Rio Grande do Sul concluiu a reconstrução das seções eleitorais afetadas pelas enchentes de 2024, garantindo que todos os eleitores gaúchos tenham local de votação para as próximas eleições.",
        "url": "https://www.tre-rs.jus.br/comunicacao/noticias/2024/reconstrucao-seccoes",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=1, hours=2)).isoformat(),
    },
    # TRE-PR
    {
        "sigla": "TRE-PR",
        "nome": "TRE do Paraná",
        "title": "TRE-PR lança aplicativo de consulta à situação eleitoral",
        "summary": "O TRE-PR disponibilizou versão atualizada do aplicativo mobile que permite aos eleitores paranaenses consultar sua situação eleitoral, local de votação e emitir certidões de quitação.",
        "url": "https://www.tre-pr.jus.br/comunicacao/noticias/2024/app-situacao-eleitoral",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
    },
    # TRE-BA
    {
        "sigla": "TRE-BA",
        "nome": "TRE da Bahia",
        "title": "TRE-BA promove semana da democracia com eventos em Salvador",
        "summary": "O Tribunal Regional Eleitoral da Bahia realizará a Semana da Democracia com palestras, exposições e atividades interativas sobre cidadania e participação política para estudantes e cidadãos em geral.",
        "url": "https://www.tre-ba.jus.br/comunicacao/noticias/2024/semana-democracia",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat(),
    },
    # TRE-CE
    {
        "sigla": "TRE-CE",
        "nome": "TRE do Ceará",
        "title": "TRE-CE realiza atendimento itinerante em municípios do interior",
        "summary": "O TRE-CE levará serviços eleitorais a 30 municípios do interior cearense através do projeto Justiça Eleitoral Itinerante, beneficiando eleitores que têm dificuldade de acesso às zonas eleitorais.",
        "url": "https://www.tre-ce.jus.br/comunicacao/noticias/2024/atendimento-itinerante",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=2, hours=6)).isoformat(),
    },
    # TRE-PE
    {
        "sigla": "TRE-PE",
        "nome": "TRE de Pernambuco",
        "title": "TRE-PE e Seduc firmam parceria para educação eleitoral nas escolas",
        "summary": "O Tribunal Regional Eleitoral de Pernambuco assinou acordo com a Secretaria de Educação do estado para implementar o programa de educação para a democracia em todas as escolas da rede pública estadual.",
        "url": "https://www.tre-pe.jus.br/comunicacao/noticias/2024/parceria-seduc",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
    },
    # TRE-GO
    {
        "sigla": "TRE-GO",
        "nome": "TRE de Goiás",
        "title": "TRE-GO divulga calendário eleitoral para municípios goianos",
        "summary": "O Tribunal Regional Eleitoral de Goiás divulgou o calendário eleitoral completo para os municípios do estado, com datas importantes para candidaturas, campanhas e votação.",
        "url": "https://www.tre-go.jus.br/comunicacao/noticias/2024/calendario-eleitoral",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    },
    # TRE-DF
    {
        "sigla": "TRE-DF",
        "nome": "TRE do Distrito Federal",
        "title": "TRE-DF inaugura posto avançado de atendimento no Gama",
        "summary": "O Tribunal Regional Eleitoral do Distrito Federal inaugurou posto avançado de atendimento eleitoral na cidade-satélite do Gama, ampliando o acesso dos eleitores distritais aos serviços de alistamento e transferência.",
        "url": "https://www.tre-df.jus.br/comunicacao/noticias/2024/posto-avancado-gama",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
    },
    # TRE-SC
    {
        "sigla": "TRE-SC",
        "nome": "TRE de Santa Catarina",
        "title": "TRE-SC realiza simulado de eleições para alunos do ensino médio",
        "summary": "O TRE de Santa Catarina realizou simulado de eleições para estudantes do ensino médio em Florianópolis, proporcionando experiência prática com urnas eletrônicas e o processo democrático de votação.",
        "url": "https://www.tre-sc.jus.br/comunicacao/noticias/2024/simulado-eleicoes",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),
    },
    # TRE-PA
    {
        "sigla": "TRE-PA",
        "nome": "TRE do Pará",
        "title": "TRE-PA leva atendimento eleitoral a comunidades ribeirinhas",
        "summary": "O Tribunal Regional Eleitoral do Pará realizará operação especial de atendimento eleitoral a comunidades ribeirinhas e de difícil acesso no interior do estado, utilizando embarcações para alcançar eleitores isolados.",
        "url": "https://www.tre-pa.jus.br/comunicacao/noticias/2024/comunidades-ribeirinhas",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    },
    # TRE-AM
    {
        "sigla": "TRE-AM",
        "nome": "TRE do Amazonas",
        "title": "TRE-AM implementa votação em trânsito para servidores em missão",
        "summary": "O TRE-AM regulamentou o procedimento de votação em trânsito para servidores públicos que estiverem em missão oficial fora de seu domicílio eleitoral no dia das eleições.",
        "url": "https://www.tre-am.jus.br/comunicacao/noticias/2024/votacao-transito",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
    },
    # TRE-MT
    {
        "sigla": "TRE-MT",
        "nome": "TRE do Mato Grosso",
        "title": "TRE-MT expande biometria a municípios do médio-norte",
        "summary": "O Tribunal Regional Eleitoral do Mato Grosso está expandindo o cadastramento biométrico a municípios da região do médio-norte do estado, com equipes itinerantes percorrendo as cidades.",
        "url": "https://www.tre-mt.jus.br/comunicacao/noticias/2024/biometria-medio-norte",
        "image_url": None,
        "published": (datetime.now(timezone.utc) - timedelta(days=4)).isoformat(),
    },
]


def populate_demo():
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from scraper import init_db, save_articles

    init_db()
    saved = save_articles(DEMO_NEWS)
    print(f"Dados de demonstração inseridos: {saved} novas notícias")
    return saved


if __name__ == "__main__":
    populate_demo()
