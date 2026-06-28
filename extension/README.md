# PJe TRE-CE — Exportar CSV

Extensão para Chrome e Firefox que exporta os resultados de qualquer consulta de processos do PJe TRE-CE para um arquivo `.csv`.

## Como instalar (modo desenvolvedor)

### Chrome / Edge

1. Abra `chrome://extensions`
2. Ative **Modo do desenvolvedor** (canto superior direito)
3. Clique em **Carregar sem compactação**
4. Selecione a pasta `extension/`

### Firefox

1. Abra `about:debugging#/runtime/this-firefox`
2. Clique em **Carregar extensão temporária**
3. Selecione o arquivo `extension/manifest.json`

> Para instalação permanente no Firefox, é necessário assinar a extensão via [addons.mozilla.org](https://addons.mozilla.org/).

## Como usar

1. Acesse o PJe TRE-CE e execute uma consulta de processos
2. Quando a lista de resultados aparecer, clique no ícone da extensão
3. Clique em **Exportar CSV**
4. O arquivo será baixado automaticamente com BOM UTF-8 (compatível com Excel)

## Domínios cobertos

| Ambiente | URL |
|---|---|
| 1º Grau | `pje1g-ce.tse.jus.br` |
| 2º Grau | `pje.tre-ce.jus.br` |

## Estrutura

```
extension/
├── manifest.json   # Manifesto MV3 (Chrome + Firefox 109+)
├── content.js      # Detecta tabelas, extrai dados, gera download
├── popup.html      # Interface do botão de exportação
├── popup.js        # Lógica do popup + chamada ao content script
├── popup.css       # Estilos
└── icons/          # Ícones 16×16, 48×48, 128×128
```
