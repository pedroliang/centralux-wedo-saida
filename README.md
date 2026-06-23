# Centralux • Saída Diária

Site para consultar os produtos e suas quantidades (Soma do SKU) da aba **Saída Diária** da planilha do Google Sheets.

## O que dá pra fazer
- **Pesquisar** por nome do produto ou SKU.
- **Filtrar por data** (ou ver todas as datas somadas).
- **Filtrar por logística** solicitada pelo comprador.
- Ver os **gráficos Top 10 melhores e piores** produtos por quantidade.
- Tabela com SKU, descrição, logística e a Soma (coluna H).

## Como os dados funcionam
- Os dados vêm das colunas **G (SKU)** e **H (Soma)** da planilha, agrupados por data.
- A descrição é obtida pela coluna **B** (mapeada pelo SKU da coluna **C**).
- A logística vem da coluna **D**.
- O arquivo `data.json` é a cópia usada pelo site.
- Uma **GitHub Action** (`.github/workflows/update-data.yml`) roda **todo dia** e regenera o `data.json` a partir da planilha. Também dá pra rodar na hora em **Actions → Atualizar dados da planilha → Run workflow**.

## Atualizar manualmente (local)
```bash
python parse_sheet.py        # busca a planilha online e gera data.json
```

## Fonte
[Planilha no Google Sheets](https://docs.google.com/spreadsheets/d/195akgdyA1wWWeTfR4MOjRb84onEb5OmPWBW13TiTBkE/edit?gid=2022201557)
