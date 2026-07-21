"""Renderização do relatório de análise em Markdown.

Segue o fluxo do art. 74 da Res. 23.607/2019: se houver achado pendente de
diligência, o documento gerado é um relatório de diligências recomendando a
intimação da prestadora/do prestador de contas (arts. 66, 69 e 72) — o
parecer conclusivo só é renderizado quando não houver mais nenhuma pendência.
"""

from __future__ import annotations

from .achados import Severidade
from .analisador import Relatorio

_ICONE_SEVERIDADE = {
    Severidade.GRAVE: "🔴",
    Severidade.IRREGULARIDADE: "🟠",
    Severidade.ALERTA: "🟡",
    Severidade.INFO: "🔵",
}


def _cabecalho(relatorio: Relatorio) -> list[str]:
    pc = relatorio.prestacao
    cand = pc.candidato_ou_comite
    return [
        f"- **Cargo:** {cand.cargo.value} — {cand.municipio}/{cand.uf}",
        f"- **Data da eleição:** {pc.data_eleicao.isoformat()}",
        f"- **Data de apresentação das contas:** "
        f"{pc.data_apresentacao.isoformat() if pc.data_apresentacao else 'NÃO APRESENTADA'}",
        f"- **Total de receitas:** R$ {pc.total_receitas}",
        f"- **Total de despesas:** R$ {pc.total_despesas}",
    ]


def _listar_achados(achados, titulo_secao: str) -> list[str]:
    linhas = [f"## {titulo_secao}", ""]
    if not achados:
        linhas.append("Nenhum item nesta categoria.")
        return linhas
    for severidade in (Severidade.GRAVE, Severidade.IRREGULARIDADE, Severidade.ALERTA, Severidade.INFO):
        do_grupo = [a for a in achados if a.severidade == severidade]
        if not do_grupo:
            continue
        linhas.append(f"### {_ICONE_SEVERIDADE[severidade]} {severidade.value} ({len(do_grupo)})")
        linhas.append("")
        for a in do_grupo:
            item = f" (item: `{a.item_relacionado_id}`)" if a.item_relacionado_id else ""
            linhas.append(f"- **{a.titulo}**{item} — {a.descricao}")
            linhas.append(f"  - *Referência:* {a.referencia_normativa} · *regra:* `{a.regra}`")
        linhas.append("")
    return linhas


def renderizar_markdown(relatorio: Relatorio) -> str:
    pc = relatorio.prestacao
    cand = pc.candidato_ou_comite
    linhas = [f"# Análise de contas eleitorais — {cand.nome}", ""]
    linhas += _cabecalho(relatorio)
    linhas.append("")

    if not relatorio.pronto_para_parecer_conclusivo:
        linhas += [
            "## ⚠️ Relatório de diligências — parecer conclusivo ainda NÃO deve ser elaborado",
            "",
            "Há achados sobre os quais a prestadora/o prestador de contas ainda não teve "
            "oportunidade de se manifestar. Nos termos dos arts. 66, 69 e 72 da "
            "Res.-TSE 23.607/2019, a providência cabível nesta fase é determinar diligência "
            "e **intimar a prestadora/o prestador de contas** para, no prazo de 3 (três) dias, "
            "manifestar-se sobre os pontos abaixo — o parecer conclusivo (art. 74) só deve ser "
            "elaborado após essa manifestação (ou o decurso do prazo sem resposta).",
            "",
        ]
        linhas += _listar_achados(
            relatorio.achados_pendentes_diligencia, "Pontos que exigem diligência/intimação"
        )
        if relatorio.achados_sanados:
            linhas += _listar_achados(relatorio.achados_sanados, "Achados já sanados em diligência anterior")
        return "\n".join(linhas)

    linhas += [
        f"- **Parecer sugerido:** {relatorio.parecer_sugerido}",
        "",
        "> ⚠️ Parecer sugerido apenas para triagem automatizada. O julgamento "
        "formal das contas é ato do órgão competente da Justiça Eleitoral, "
        "à luz do conjunto das circunstâncias e da versão vigente da "
        "Resolução TSE nº 23.607/2019 (art. 74).",
        "",
    ]
    linhas += _listar_achados(relatorio.achados_confirmados, "Achados confirmados (após diligência)")
    if relatorio.achados_sanados:
        linhas += _listar_achados(relatorio.achados_sanados, "Achados sanados em diligência")

    return "\n".join(linhas)
