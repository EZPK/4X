"""L'économie d'une partie, par fenêtre (docs/designs/niveau-2-m1-noyau.md, Technical Plan,
point 9 ; plan détaillé, point 28).

Lit le fichier `events.jsonl` d'une partie, appelle `window_stats` (fenêtres de 10 000 ticks par
défaut) et affiche par fenêtre la masse monétaire, sa croissance, l'émission et la destruction par
motif. Il lit aussi les événements avec DuckDB pour les explorer, sans calculer lui-même ces
grandeurs. Lancement :

    uv run --group notebooks marimo edit notebooks/economie_m1.py
"""

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo

    return Path, mo


@app.cell
def _(Path, mo):
    _parties = sorted(Path("runs").glob("*/events.jsonl"))
    chemin = mo.ui.text(
        value=str(_parties[-1]) if _parties else "runs/<dossier de partie>/events.jsonl",
        label="Fichier events.jsonl",
        full_width=True,
    )
    fenetre = mo.ui.number(start=1, value=10_000, step=1_000, label="Fenêtre (ticks)")
    mo.vstack([chemin, fenetre])
    return chemin, fenetre


@app.cell
def _(Path, chemin, fenetre, mo):
    import msgspec

    from fourx.schema.events import Event
    from fourx.tools.economy import MOTIFS, window_stats

    fichier = Path(chemin.value)
    mo.stop(not fichier.is_file(), mo.md(f"Fichier introuvable : `{fichier}`"))
    _decodeur = msgspec.json.Decoder(Event)
    evenements = [_decodeur.decode(_l) for _l in fichier.read_bytes().splitlines() if _l.strip()]
    fenetres = window_stats(evenements, int(fenetre.value))
    return MOTIFS, fenetres, fichier


@app.cell
def _(MOTIFS, fenetres, mo):
    _lignes = [
        {
            "premier tick": _f.first_tick,
            **{f"émission {_m.value}": _f.issued_by_reason[_i] for _i, _m in enumerate(MOTIFS)},
            **{
                f"destruction {_m.value}": _f.destroyed_by_reason[_i]
                for _i, _m in enumerate(MOTIFS)
            },
            "croissance de la masse monétaire": _f.money_supply_growth,
            "masse monétaire en fin de fenêtre": _f.money_supply_end,
        }
        for _f in fenetres
    ]
    mo.vstack([mo.md("## Économie par fenêtre (`window_stats`)"), mo.ui.table(_lignes)])
    return


@app.cell
def _(fichier, mo):
    import duckdb

    _resultat = duckdb.execute(
        "SELECT payload.type AS type, count(*) AS nombre, min(tick) AS premier_tick, "
        "max(tick) AS dernier_tick FROM read_json_auto(?) GROUP BY 1 ORDER BY 2 DESC",
        [str(fichier)],
    )
    _colonnes = [_d[0] for _d in _resultat.description]
    _lignes = [dict(zip(_colonnes, _r, strict=True)) for _r in _resultat.fetchall()]
    mo.vstack([mo.md("## Événements par type (DuckDB, exploration)"), mo.ui.table(_lignes)])
    return


if __name__ == "__main__":
    app.run()
