#!/usr/bin/env python3
"""Le a aba 'Saida Diaria' da planilha do Google e gera data.json.
Fonte: colunas G (SKU) e H (Soma) = total por SKU em cada data.
Descricao vem da coluna B (mapeada pelo SKU da coluna C).
Logistica vem da coluna D (coluna detalhe)."""
import csv, re, json, sys, io, urllib.request, datetime

SHEET_ID = "195akgdyA1wWWeTfR4MOjRb84onEb5OmPWBW13TiTBkE"
GID = "2022201557"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

MONTHS = {"janeiro":1,"fevereiro":2,"marco":3,"março":3,"abril":4,"maio":5,
          "junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,
          "novembro":11,"dezembro":12}
date_re = re.compile(r'^(\d{1,2})/(\d{1,2})')

def load_rows(path=None):
    if path:
        return list(csv.reader(open(path, encoding="utf-8")))
    data = urllib.request.urlopen(CSV_URL, timeout=60).read().decode("utf-8")
    return list(csv.reader(io.StringIO(data)))

def parse(rows):
    cur_month = None
    cur_date = None          # "dd/mm"
    cur_year = datetime.date.today().year
    # detalhe global: sku -> descricao (mais frequente)
    desc_counts = {}
    # por data: detalhe left  -> sku -> {qty, logistics{ name:qty }}
    # por data: resumo right  -> sku -> soma (coluna H)
    left = {}   # date -> sku -> {"qty":int, "log":{name:qty}}
    right = {}  # date -> sku -> soma
    date_order = []

    for r in rows:
        g = lambda i: (r[i].strip() if len(r) > i else "")
        A,B,C,D,E,F,G,H = [g(i) for i in range(8)]
        low = A.lower().strip()
        if low in MONTHS:
            cur_month = MONTHS[low]; continue
        m = date_re.match(A)
        if m:
            dd, mm = int(m.group(1)), int(m.group(2))
            cur_date = f"{dd:02d}/{mm:02d}"
            if cur_date not in left:
                left[cur_date] = {}; right[cur_date] = {}
                date_order.append((cur_year, mm, dd, cur_date))
            continue
        # left detail
        if B and C and C.isdigit() and B != "Nome do produto":
            try: q = int(float(E)) if E else 0
            except: q = 0
            desc_counts.setdefault(C, {}).setdefault(B, 0)
            desc_counts[C][B] += 1
            if cur_date:
                d = left[cur_date].setdefault(C, {"qty":0,"log":{}})
                d["qty"] += q
                if D:
                    d["log"][D] = d["log"].get(D, 0) + q
        # right summary (autoritativo)
        if G and G.isdigit() and H and cur_date:
            try: s = int(float(H))
            except:
                continue
            right[cur_date][G] = right[cur_date].get(G, 0) + s

    sku_desc = {sku: max(v.items(), key=lambda x:x[1])[0] for sku,v in desc_counts.items()}

    records = []
    for (yy,mm,dd,dlabel) in date_order:
        skus = set(right[dlabel]) | set(left[dlabel])
        for sku in skus:
            soma = right[dlabel].get(sku)
            ldet = left[dlabel].get(sku, {"qty":0,"log":{}})
            if soma is None:
                soma = ldet["qty"]
            log = [{"name":n,"qty":q} for n,q in sorted(ldet["log"].items(), key=lambda x:-x[1])]
            records.append({
                "date": dlabel, "sku": sku,
                "desc": sku_desc.get(sku, f"SKU {sku}"),
                "soma": soma,
                "logistics": log,
            })

    dates = [d[3] for d in date_order]
    return {
        "generatedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "sourceUrl": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid={GID}",
        "dates": dates,
        "skuDesc": sku_desc,
        "records": records,
    }

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    rows = load_rows(path)
    out = parse(rows)
    json.dump(out, open("data.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    print("dates:", len(out["dates"]), out["dates"])
    print("records:", len(out["records"]))
    print("skus:", len(out["skuDesc"]))
