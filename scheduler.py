"""
scheduler.py - Workflow d'automatisation Social Media Intelligence
Agence X - Pipeline automatisé : Collecte → Traitement → Rapport → Mise à jour

Usage :
    python scheduler.py              # Lance le scheduler en continu
    python scheduler.py --run-once   # Exécute une seule fois et quitte
"""

import schedule
import time
import logging
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le chemin src pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.preprocessing import load_and_clean_data
from src.analysis import calculate_kpis, generate_insights

# ─── Configuration du logging ────────────────────────────────────────────────
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scheduler.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ─── Chemins de données ───────────────────────────────────────────────────────
DATA_DIR    = Path("data")
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

RAW_DATA_PATH    = DATA_DIR / "raw_data.csv"
REPORT_JSON_PATH = REPORTS_DIR / "latest_report.json"
REPORT_TXT_PATH  = REPORTS_DIR / "latest_report.txt"


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 1 — Collecte des données
# ════════════════════════════════════════════════════════════════════════════════
def step_collect() -> bool:
    """
    Simule la collecte automatique depuis une source externe.
    En production : remplacer par un appel API réel (Instagram Graph API,
    Twitter/X API, TikTok API, etc.).
    """
    logger.info("━━━ ÉTAPE 1 : Collecte des données ━━━")

    if not RAW_DATA_PATH.exists():
        logger.error(f"Fichier source introuvable : {RAW_DATA_PATH}")
        return False

    # Simuler une mise à jour : horodatage dans les métadonnées
    meta_path = DATA_DIR / "collection_meta.json"
    meta = {
        "last_collection": datetime.now().isoformat(),
        "source": "Kaggle dataset (simulation — remplacer par API en prod)",
        "file": str(RAW_DATA_PATH),
        "status": "success",
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    logger.info(f"Métadonnées de collecte sauvegardées → {meta_path}")
    return True


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 2 — Nettoyage & Préparation
# ════════════════════════════════════════════════════════════════════════════════
def step_clean():
    """Charge et nettoie les données brutes via preprocessing.py."""
    logger.info("━━━ ÉTAPE 2 : Nettoyage & Préparation ━━━")
    df = load_and_clean_data(str(RAW_DATA_PATH))
    logger.info(f"Données nettoyées : {len(df):,} lignes × {len(df.columns)} colonnes")
    return df


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 3 — Analyse & KPIs
# ════════════════════════════════════════════════════════════════════════════════
def step_analyze(df):
    """Calcule les KPIs et génère les insights."""
    logger.info("━━━ ÉTAPE 3 : Analyse & KPIs ━━━")
    kpis, df = calculate_kpis(df)
    insights = generate_insights(df)

    logger.info(f"  Total posts     : {kpis.get('total_posts', 0):,}")
    logger.info(f"  Engagement total: {kpis.get('total_engagement', 0):,}")
    logger.info(f"  Engagement moyen: {kpis.get('avg_engagement', 0):.0f}")
    logger.info(f"  Meilleure plateforme: {kpis.get('best_platform', 'N/A')}")
    logger.info(f"  Insights générés: {len(insights)}")

    return kpis, insights, df


# ════════════════════════════════════════════════════════════════════════════════
# ÉTAPE 4 — Sauvegarde du rapport
# ════════════════════════════════════════════════════════════════════════════════
def step_save_report(kpis: dict, insights: list):
    """Sauvegarde le rapport en JSON et en TXT pour traçabilité."""
    logger.info("━━━ ÉTAPE 4 : Sauvegarde du rapport ━━━")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # — Rapport JSON (pour intégration API ou tableau de bord) —
    report_json = {
        "generated_at": now_str,
        "kpis": kpis,
        "insights": insights,
    }
    REPORT_JSON_PATH.write_text(
        json.dumps(report_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # — Rapport TXT lisible —
    lines = [
        "=" * 60,
        "   RAPPORT AUTOMATIQUE — SOCIAL MEDIA INTELLIGENCE",
        "=" * 60,
        f"Généré le : {now_str}",
        "",
        "── KPIs ──────────────────────────────────────────────",
        f"  Total posts         : {kpis.get('total_posts', 0):,}",
        f"  Engagement total    : {kpis.get('total_engagement', 0):,}",
        f"  Engagement moyen    : {kpis.get('avg_engagement', 0):.0f}",
        f"  Meilleure plateforme: {kpis.get('best_platform', 'N/A')}",
        f"  Meilleur contenu    : {kpis.get('best_content_type', 'N/A')}",
        "",
        "── INSIGHTS ──────────────────────────────────────────",
    ]
    for insight in insights:
        lines.append(f"  • {insight}")

    lines += [
        "",
        "=" * 60,
        "Prochain rapport automatique dans 1 heure.",
        "=" * 60,
    ]

    REPORT_TXT_PATH.write_text("\n".join(lines), encoding="utf-8")

    logger.info(f"Rapport JSON → {REPORT_JSON_PATH}")
    logger.info(f"Rapport TXT  → {REPORT_TXT_PATH}")

    # Archive horodatée dans reports/
    archive_path = REPORTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    archive_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Archive      → {archive_path}")


# ════════════════════════════════════════════════════════════════════════════════
# PIPELINE COMPLET
# ════════════════════════════════════════════════════════════════════════════════
def run_pipeline():
    """Exécute le pipeline complet : Collecte → Nettoyage → Analyse → Rapport."""
    start = datetime.now()
    logger.info("")
    logger.info("╔══════════════════════════════════════════════╗")
    logger.info("║    PIPELINE AUTOMATISÉ — DÉMARRAGE           ║")
    logger.info(f"║    {start.strftime('%Y-%m-%d %H:%M:%S')}                    ║")
    logger.info("╚══════════════════════════════════════════════╝")

    try:
        # Étape 1 : Collecte
        if not step_collect():
            logger.error("Pipeline interrompu à l'étape Collecte.")
            return

        # Étape 2 : Nettoyage
        df = step_clean()
        if df.empty:
            logger.error("Pipeline interrompu : dataframe vide après nettoyage.")
            return

        # Étape 3 : Analyse
        kpis, insights, df = step_analyze(df)

        # Étape 4 : Rapport
        step_save_report(kpis, insights)

        elapsed = (datetime.now() - start).total_seconds()
        logger.info("")
        logger.info(f"✅ Pipeline terminé en {elapsed:.1f}s — prochain run dans 1h.")
        logger.info("")

    except Exception as exc:
        logger.exception(f"❌ Erreur inattendue dans le pipeline : {exc}")


# ════════════════════════════════════════════════════════════════════════════════
# SCHEDULER
# ════════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Scheduler d'automatisation Social Media Intelligence"
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Exécuter le pipeline une seule fois puis quitter",
    )
    args = parser.parse_args()

    if args.run_once:
        logger.info("Mode --run-once : exécution unique.")
        run_pipeline()
        return

    # ── Mode scheduler continu ──────────────────────────────────────────────
    logger.info("Scheduler démarré.")
    logger.info("  • Pipeline toutes les heures")
    logger.info("  • Rapport quotidien à 08:00")
    logger.info("  Ctrl+C pour arrêter.\n")

    # Exécution immédiate au démarrage
    run_pipeline()

    # Planifications récurrentes
    schedule.every(1).hours.do(run_pipeline)            # toutes les heures
    schedule.every().day.at("08:00").do(run_pipeline)   # rapport matinal

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)   # vérifie toutes les 30s
    except KeyboardInterrupt:
        logger.info("Scheduler arrêté proprement (Ctrl+C).")


if __name__ == "__main__":
    main()