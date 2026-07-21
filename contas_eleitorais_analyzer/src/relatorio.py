"""Renderização do relatório de análise em Markdown."""

from __future__ import annotations

from .achados import Severidade
from .analisador import Relatorio

_ICONE_SEVERIDADE = {
    Severidade.GRAVE: "🔴",
    Severidade.IRREGULARIDADE: "🟠",
    Severidade.ALERTA: "🟡",
    Severidade.INFO: "🔵",
}


def renderizar_markdown(relatorio: Relatorio) -> str:
    pc = relatorio.prestacao
    cand = pc.candidato_ou_comite
    linhas = [
        f"# Relatório de análise de contas eleitorais — {cand.nome}",
        "",
        f"- **Cargo:** {cand.cargo.value} — {cand.municipio}/{cand.uf}",
        f"- **Data da eleição:** {pc.data_eleicao.isoformat()}",
        f"- **Data de apresentação das contas:** "
        f"{pc.data_apresentacao.isoformat() if pc.data_apresentacao else 'NÃO APRESENTADA'}",
        f"- **Total de receitas:** R$ {pc.total_receitas}",
        f"- **Total de despesas:** R$ {pc.total_despesas}",
        f"- **Parecer sugerido:** {relatorio.parecer_sugerido}",
        "",
        "> ⚠️ Parecer sugerido apenas para triagem automatizada. O julgamento "
        "formal das contas é ato do órgão competente da Justiça Eleitoral, "
        "à luz do conjunto das circunstâncias e da versão vigente da "
        "Resolução TSE nº 23.607/2019.",
        "",
        "## Achados",
        "",
    ]

    if not relatorio.achados:
        linhas.append("Nenhuma pendência identificada pelas regras aplicadas.")
    else:
        for severidade in (Severidade.GRAVE, Severidade.IRREGULARIDADE, Severidade.ALERTA, Severidade.INFO):
            achados_sev = relatorio.achados_por_severidade(severidade)
            if not achados_sev:
                continue
            linhas.append(f"### {_ICONE_SEVERIDADE[severidade]} {severidade.value} ({len(achados_sev)})")
            linhas.append("")
            for a in achados_sev:
                item = f" (item: `{a.item_relacionado_id}`)" if a.item_relacionado_id else ""
                linhas.append(f"- **{a.titulo}**{item} — {a.descricao}")
                linhas.append(f"  - *Referência:* {a.referencia_normativa} · *regra:* `{a.regra}`")
            linhas.append("")

    return "\n".join(linhas)
