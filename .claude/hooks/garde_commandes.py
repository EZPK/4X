"""Hook `PreToolUse` de Claude Code sur l'outil Bash.

Niveau 2 de M0 : Technical Plan, points 3 et 6 ; plan détaillé, point 33.
Lit l'appel d'outil en JSON sur l'entrée standard. Code 0 : la commande passe. Code 2 : refus,
avec un message en français sur la sortie d'erreur. Toute erreur et tout doute donnent un refus.
Bibliothèque standard seulement. Le hook ne voit pas ce que fait un script lancé par l'agent.
"""

import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
ETIQUETTE = "fichiers protégés modifiés"

AMORCAGE_SECURITE = "gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json"
AMORCAGE_PUSH = "git push -u origin main"
AMORCAGE_PROTECTION = (
    "gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json"
)

# Copies de référence des points 21 et 22 du plan détaillé, comparées après `json.load`.
REFERENCE_SECURITE: dict[str, object] = {
    "security_and_analysis": {
        "secret_scanning": {"status": "enabled"},
        "secret_scanning_push_protection": {"status": "enabled"},
    }
}
REFERENCE_PROTECTION: dict[str, object] = {
    "required_status_checks": {
        "strict": True,
        "contexts": [
            "lint",
            "typage",
            "gitleaks",
            "termes-interdits",
            "tests-outillage",
            "garde",
            "en-attente",
        ],
    },
    "enforce_admins": True,
    "required_pull_request_reviews": {"required_approving_review_count": 0},
    "restrictions": None,
    "allow_force_pushes": False,
    "allow_deletions": False,
}

REGLE_FUSION = (
    "CLAUDE.md, « Ne jamais » : fusionner une pull request, même avec --admin, "
    "ni activer la fusion automatique (--auto). Seul le propriétaire fusionne"
)
REGLE_PUSH = "CLAUDE.md, « Ne jamais » : pousser vers main, forcer un push"
REGLE_PRECOMMIT = (
    "CLAUDE.md, « Ne jamais » : utiliser --no-verify ; tout contournement du hook pre-commit "
    "est refusé"
)
REGLE_REGLAGES = (
    "CLAUDE.md, « Ne jamais » : modifier la protection de branche, les ensembles de règles "
    "ou les réglages du dépôt ; les écritures sur GitHub passent par une liste blanche"
)
REGLE_DOUTE = "hook Claude Code : en cas de doute, la commande est refusée (M0, Technical Plan, 6)"

OPTIONS_GIT_AVEC_VALEUR = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
OPTIONS_GIT_SANS_VALEUR = {
    "--no-pager",
    "-P",
    "-p",
    "--paginate",
    "--bare",
    "--no-replace-objects",
    "--literal-pathspecs",
    "--glob-pathspecs",
    "--noglob-pathspecs",
    "--icase-pathspecs",
    "--no-optional-locks",
    "--no-advice",
}
PUSH_INTERDITS = {
    "--force",
    "--force-with-lease",
    "--force-if-includes",
    "--mirror",
    "--all",
    "--branches",
    "--delete",
    "--prune",
}
PUSH_AVEC_VALEUR = {"--repo", "--push-option", "--receive-pack", "--exec"}
PUSH_PERMIS = PUSH_AVEC_VALEUR | {
    "--set-upstream",
    "--quiet",
    "--verbose",
    "--dry-run",
    "--tags",
    "--follow-tags",
    "--no-follow-tags",
    "--atomic",
    "--no-atomic",
    "--porcelain",
    "--progress",
    "--no-progress",
    "--verify",
    "--ipv4",
    "--ipv6",
    "--thin",
    "--no-thin",
    "--signed",
    "--no-signed",
    "--recurse-submodules",
    "--no-recurse-submodules",
}
COMMIT_LONGUES_AVEC_VALEUR = {
    "--author",
    "--date",
    "--reuse-message",
    "--reedit-message",
    "--fixup",
    "--squash",
    "--template",
    "--cleanup",
    "--pathspec-from-file",
    "--trailer",
}

API_AVEC_VALEUR = {
    "-H",
    "--header",
    "-q",
    "--jq",
    "-t",
    "--template",
    "--cache",
    "--hostname",
    "-p",
    "--preview",
}
API_SANS_VALEUR = {"--paginate", "--slurp", "-i", "--include", "--silent", "--verbose"}
API_CHAMPS = {"-f", "-F", "--field", "--raw-field"}

# Écritures permises par `gh api`, sur les routes de `repos/EZPK/4X/`.
ECRITURES: list[tuple[str, str]] = [
    ("POST", r"issues"),
    ("PATCH", r"issues/\d+"),
    ("POST", r"issues/\d+/comments"),
    ("POST", r"issues/\d+/labels"),
    ("PATCH", r"issues/comments/\d+"),
    ("POST", r"milestones"),
    ("PATCH", r"milestones/\d+"),
    ("POST", r"labels"),
    ("POST", r"pulls"),
    ("PATCH", r"pulls/\d+"),
    ("POST", r"pulls/\d+/comments"),
    ("PATCH", r"pulls/comments/\d+"),
    ("DELETE", r"git/refs/heads/essai/[A-Za-z0-9._/-]+"),
]

# Sous-commandes de `gh` permises, hors `api`, `pr create`, `pr edit`, `issue edit`, `repo create`.
GH_PERMIS: dict[str, set[str]] = {
    "pr": {"view", "list", "checks", "diff", "status", "comment", "create", "edit"},
    "issue": {"view", "list", "status", "create", "comment", "edit", "close", "reopen"},
    "run": {"list", "view", "watch"},
    "repo": {"view", "create"},
    "label": {"list", "create"},
    "release": {"view", "list", "download"},
    "workflow": {"list", "view"},
    "ruleset": {"list", "view", "check"},
    "auth": {"status"},
}
GH_SANS_ACTION = {"--version", "version", "--help", "-h", "help", "status", "search"}


class Refus(Exception):
    pass


class ErreurLecture(Refus):
    pass


class Etat:
    """Lecture de l'état local et de GitHub. Les tests la remplacent par une fausse."""

    def __init__(self, dossier: Path) -> None:
        self.dossier = dossier

    def lancer(self, *commande: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(commande),
            cwd=self.dossier,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def lire_json(self, relatif: str) -> object:
        return json.loads((RACINE / relatif).read_text(encoding="utf-8"))

    def statut_blocage_secrets(self) -> str | None:
        resultat = self.lancer("gh", "api", "repos/EZPK/4X")
        if resultat.returncode != 0:
            raise ErreurLecture("lecture des réglages du dépôt en échec")
        donnees = json.loads(resultat.stdout)
        analyse = donnees.get("security_and_analysis") or {}
        statut = (analyse.get("secret_scanning_push_protection") or {}).get("status")
        return statut if isinstance(statut, str) else None

    def main_distante_absente(self) -> bool:
        resultat = self.lancer("git", "ls-remote", "--heads", "origin", "main")
        if resultat.returncode != 0:
            raise ErreurLecture("lecture de la branche main distante en échec")
        return resultat.stdout.strip() == ""

    def protection_absente(self) -> bool:
        resultat = self.lancer("gh", "api", "repos/EZPK/4X/branches/main/protection")
        if resultat.returncode == 0:
            return False
        if "Branch not protected (HTTP 404)" in resultat.stderr:
            return True
        raise ErreurLecture("lecture de la protection de main en échec")

    def depot_existe(self) -> bool:
        resultat = self.lancer("gh", "api", "repos/EZPK/4X")
        if resultat.returncode == 0:
            return True
        if "Not Found (HTTP 404)" in resultat.stderr:
            return False
        raise ErreurLecture("lecture du dépôt en échec")

    def hook_precommit_present(self) -> bool:
        if self.lancer("git", "config", "--get", "core.hooksPath").returncode == 0:
            return False
        # Dans un worktree lié, les hooks vivent dans le dossier git commun au dépôt.
        resultat = self.lancer("git", "rev-parse", "--path-format=absolute", "--git-common-dir")
        if resultat.returncode != 0:
            raise ErreurLecture("dossier .git introuvable")
        hook = Path(resultat.stdout.strip()) / "hooks" / "pre-commit"
        # Git ignore un hook sans bit d'exécution : il ne compte pas.
        return (
            hook.is_file()
            and os.access(hook, os.X_OK)
            and "pre-commit" in hook.read_text(encoding="utf-8", errors="replace")
        )

    def branche_courante(self) -> str:
        resultat = self.lancer("git", "symbolic-ref", "--short", "HEAD")
        if resultat.returncode != 0:
            raise ErreurLecture("branche courante introuvable")
        return resultat.stdout.strip()

    def amont(self) -> str | None:
        resultat = self.lancer("git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
        return resultat.stdout.strip() if resultat.returncode == 0 else None

    def config_push_risquee(self) -> bool:
        defaut = self.lancer("git", "config", "--get", "push.default")
        if defaut.returncode == 0 and defaut.stdout.strip() not in {"simple", "current", "nothing"}:
            return True
        return self.lancer("git", "config", "--get-regexp", r"^remote\..*\.push$").returncode == 0


def refuser(raison: str, regle: str) -> Refus:
    return Refus(f"{raison} ({regle})")


# --- Analyse de la chaîne brute ---------------------------------------------------------------

MOTIFS_BRUTS: list[tuple[str, str, str]] = [
    (r"\bgh\s+pr\s+merge\b", "fusion de pull request", REGLE_FUSION),
    (r"--no-verify", "option --no-verify", REGLE_PRECOMMIT),
    (r"core\.hookspath", "réglage core.hooksPath", REGLE_PRECOMMIT),
    (r"(?:^|[^\w])SKIP=", "variable SKIP de pre-commit", REGLE_PRECOMMIT),
    (r"\bpre-commit\s+uninstall\b", "désinstallation du hook pre-commit", REGLE_PRECOMMIT),
    (r"\bconfig\b[^;&|\n]*\balias\.", "définition d'un alias git", REGLE_DOUTE),
    (r"\bgh\s+repo\s+(?:edit|delete|archive|rename)\b", "modification du dépôt", REGLE_REGLAGES),
]


def chercher_motifs_bruts(commande: str) -> None:
    for motif, raison, regle in MOTIFS_BRUTS:
        drapeaux = re.IGNORECASE if motif.startswith(("core", r"\bconfig")) else 0
        if re.search(motif, commande, drapeaux):
            raise refuser(raison, regle)


# --- Découpage en jetons ----------------------------------------------------------------------


def decouper(texte: str) -> list[str]:
    lexeur = shlex.shlex(texte, posix=True, punctuation_chars=True)
    lexeur.whitespace_split = True
    lexeur.commenters = ""
    try:
        return list(lexeur)
    except ValueError as erreur:
        if re.search(r"\b(?:git|gh)\b", texte):
            raise refuser("commande git ou gh impossible à analyser", REGLE_DOUTE) from erreur
        return []


def est_operateur(jeton: str) -> bool:
    return jeton != "" and all(caractere in "();<>|&" for caractere in jeton)


def nom_de_programme(jeton: str) -> str:
    return jeton.lstrip("`$({").rstrip("`)}").rsplit("/", 1)[-1]


PROGRAMMES_CHANGEANT_DE_DOSSIER = {"cd", "pushd", "popd"}
OPTIONS_CHANGEANT_DE_DOSSIER = {"--directory", "--project", "-execdir", "-okdir"}


def options_de_env(segment: list[str]) -> list[str]:
    """Options passées à `env` dans ce segment, avant la commande qu'il lance."""
    options: list[str] = []
    for rang, jeton in enumerate(segment):
        if nom_de_programme(jeton) != "env":
            continue
        for suivant in segment[rang + 1 :]:
            if suivant.startswith("-"):
                options.append(suivant)
            elif re.match(r"\w+=", suivant) is None:
                break
    return options


def contexte(texte: str, profondeur: int) -> tuple[bool, bool]:
    """Sur toute la commande, sous-chaînes comprises et avant toute autre analyse :
    (git peut viser un autre dépôt que celui du dossier courant, configuration git par variable).
    """
    if profondeur > 3:
        raise refuser("commande trop imbriquée", REGLE_DOUTE)
    ailleurs = False
    configuration = False
    segment: list[str] = []
    for jeton in [*decouper(texte), ";"]:
        if est_operateur(jeton):
            ailleurs = ailleurs or bool(options_de_env(segment))
            segment = []
            continue
        segment.append(jeton)
        if (
            nom_de_programme(jeton) in PROGRAMMES_CHANGEANT_DE_DOSSIER
            or jeton.split("=", 1)[0] in OPTIONS_CHANGEANT_DE_DOSSIER
            or (jeton == "foreach" and "submodule" in segment)
            or re.search(r"GIT_\w", jeton)
        ):
            ailleurs = True
        configuration = configuration or "GIT_CONFIG" in jeton
        if re.search(r"\s|[;&|`]|\$\(", jeton) and decouper(jeton) != [jeton]:
            ailleurs_dedans, configuration_dedans = contexte(jeton, profondeur + 1)
            ailleurs = ailleurs or ailleurs_dedans
            configuration = configuration or configuration_dedans
    return ailleurs, configuration


class Analyse:
    def __init__(self, etat: Etat, depot_ailleurs: bool, configuration: bool) -> None:
        self.etat = etat
        self.depot_ailleurs = depot_ailleurs
        self.configuration_par_variable = configuration

    def texte(self, texte: str, profondeur: int) -> None:
        if profondeur > 3:
            raise refuser("commande trop imbriquée", REGLE_DOUTE)
        jetons = decouper(texte)
        segment: list[str] = []
        for jeton in [*jetons, ";"]:
            if est_operateur(jeton):
                self.segment(segment)
                segment = []
            else:
                segment.append(jeton)
        for jeton in jetons:
            if (
                re.search(r"\s|[;&|`]|\$\(", jeton)
                and re.search(r"\b(?:git|gh)\b", jeton)
                and decouper(jeton) != [jeton]
            ):
                self.texte(jeton, profondeur + 1)

    def segment(self, jetons: list[str]) -> None:
        for rang, jeton in enumerate(jetons):
            nom = nom_de_programme(jeton)
            if nom == "gh":
                self.gh(jetons[rang + 1 :])
            elif nom == "git":
                self.git(jetons[rang + 1 :])
            elif nom in {"git-commit", "git-push"}:
                raise refuser(f"programme « {nom} » lancé directement", REGLE_DOUTE)

    # --- gh ---

    def gh(self, arguments: list[str]) -> None:
        reste = sauter_depot(arguments)
        if not reste or reste[0] in GH_SANS_ACTION:
            return
        sous = reste[0]
        if sous == "api":
            self.api(reste[1:])
            return
        if sous not in GH_PERMIS:
            raise refuser(f"sous-commande « gh {sous} » hors liste blanche", REGLE_REGLAGES)
        actions = sauter_depot(reste[1:])
        if not actions:
            return
        action = actions[0]
        if sous == "pr" and action == "merge":
            raise refuser("fusion de pull request", REGLE_FUSION)
        if action not in GH_PERMIS[sous]:
            raise refuser(f"« gh {sous} {action} » hors liste blanche", REGLE_REGLAGES)
        options = actions[1:]
        if action == "edit":
            verifier_retrait_etiquette(options)
        if sous == "pr" and action == "create":
            verifier_creation_pr(options)
        if sous == "repo" and action == "create":
            self.creation_depot(options)

    def creation_depot(self, options: list[str]) -> None:
        if "--push" in options or any(option.startswith("--push=") for option in options):
            raise refuser("« gh repo create » avec --push", REGLE_PUSH)
        noms = [option for option in options if not option.startswith("-")]
        if not noms or noms[0].lower() != "ezpk/4x":
            raise refuser("« gh repo create » hors du dépôt EZPK/4X", REGLE_REGLAGES)
        if self.etat.depot_existe():
            raise refuser("« gh repo create » alors que le dépôt existe", REGLE_REGLAGES)

    def api(self, arguments: list[str]) -> None:
        methode: str | None = None
        champs: list[str] = []
        entree = False
        point: str | None = None
        rang = 0
        while rang < len(arguments):
            argument = arguments[rang]
            if argument in {"-X", "--method"}:
                methode = valeur(arguments, rang)
                rang += 2
                continue
            if argument.startswith("--method="):
                methode = argument.split("=", 1)[1]
            elif argument.startswith("-X"):
                methode = argument[2:]
            elif argument in API_CHAMPS:
                champs.append(valeur(arguments, rang))
                rang += 2
                continue
            elif argument.startswith(("--field=", "--raw-field=")):
                champs.append(argument.split("=", 1)[1])
            elif argument[:2] in {"-f", "-F"}:
                champs.append(argument[2:])
            elif argument == "--input":
                valeur(arguments, rang)
                entree = True
                rang += 2
                continue
            elif argument.startswith("--input="):
                entree = True
            elif argument in API_AVEC_VALEUR:
                valeur(arguments, rang)
                rang += 2
                continue
            elif argument.split("=", 1)[0] in API_AVEC_VALEUR and "=" in argument:
                pass
            elif argument in API_SANS_VALEUR:
                pass
            elif argument.startswith("-") and argument != "-":
                raise refuser(f"option « {argument} » de gh api inconnue", REGLE_DOUTE)
            elif point is None:
                point = argument
            else:
                raise refuser("gh api avec deux points d'accès", REGLE_DOUTE)
            rang += 1
        if point is None:
            return
        chemin = re.sub(r"^https://api\.github\.com/", "", point).split("?", 1)[0].strip("/")
        if chemin.lower() == "graphql":
            raise refuser("gh api graphql", REGLE_REGLAGES)
        verbe = (methode or ("POST" if champs or entree else "GET")).upper()
        if verbe == "GET" and not champs and not entree:
            return
        if entree:
            raise refuser("gh api en écriture avec --input, hors amorçage", REGLE_REGLAGES)
        prefixe = "repos/ezpk/4x/"
        if not chemin.lower().startswith(prefixe):
            raise refuser(f"écriture GitHub sur « {chemin} »", regle_ecriture(chemin))
        route = chemin[len(prefixe) :]
        if ".." in route or not any(
            verbe == permis and re.fullmatch(motif, route) for permis, motif in ECRITURES
        ):
            raise refuser(f"écriture GitHub {verbe} sur « {chemin} »", regle_ecriture(route))
        cles = {champ.split("=", 1)[0].split("[", 1)[0] for champ in champs}
        if verbe == "PATCH" and re.fullmatch(r"issues/\d+", route) and "labels" in cles:
            raise refuser("remplacement des étiquettes d'une pull request", REGLE_REGLAGES)
        if verbe == "PATCH" and re.fullmatch(r"pulls/\d+", route):
            if not cles <= {"title", "body", "state"}:
                raise refuser(
                    "modification d'une pull request hors titre, corps, état", REGLE_REGLAGES
                )
            etats = [champ.split("=", 1)[1] for champ in champs if champ.startswith("state=")]
            if any(etat != "closed" for etat in etats):
                raise refuser("état de pull request autre que closed", REGLE_REGLAGES)

    # --- git ---

    def git(self, arguments: list[str]) -> None:
        if self.configuration_par_variable:
            raise refuser("git dans une commande qui contient GIT_CONFIG", REGLE_DOUTE)
        rang = 0
        surcharge = False
        ailleurs = False
        while rang < len(arguments) and arguments[rang].startswith("-"):
            argument = arguments[rang]
            nom = argument.split("=", 1)[0]
            if nom in {"--help", "-h", "--version"}:
                return
            if nom in OPTIONS_GIT_AVEC_VALEUR:
                reglage = argument.split("=", 1)[1] if "=" in argument else valeur(arguments, rang)
                if nom in {"-c", "--config-env"} and reglage.lower().startswith("alias."):
                    raise refuser("alias git défini en ligne de commande", REGLE_DOUTE)
                surcharge = surcharge or nom in {"-c", "--config-env"}
                ailleurs = ailleurs or nom not in {"-c", "--config-env"}
                rang += 1 if "=" in argument else 2
            elif argument in OPTIONS_GIT_SANS_VALEUR:
                rang += 1
            elif any(
                suivant in {"commit", "push"} or "alias." in suivant.lower()
                for suivant in arguments[rang + 1 :]
            ):
                raise refuser(f"option globale « {nom} » de git inconnue", REGLE_DOUTE)
            else:
                return
        if rang >= len(arguments):
            return
        sous = arguments[rang]
        reste = arguments[rang + 1 :]
        if sous == "push":
            self.push(reste, surcharge, ailleurs)
        elif sous == "commit":
            if surcharge:
                raise refuser("git -c avec git commit", REGLE_DOUTE)
            if ailleurs or self.depot_ailleurs:
                raise refuser(
                    "git commit : la commande peut viser un autre dépôt que celui du dossier "
                    "courant",
                    REGLE_DOUTE,
                )
            self.commit(reste)

    def commit(self, arguments: list[str]) -> None:
        avec_message = False
        rang = 0
        while rang < len(arguments):
            argument = arguments[rang]
            if argument == "--":
                break
            if argument.startswith("--"):
                nom = argument.split("=", 1)[0]
                if nom in {"--message", "--file"}:
                    avec_message = True
                    rang += 1 if "=" in argument else 2
                    continue
                if nom in COMMIT_LONGUES_AVEC_VALEUR and "=" not in argument:
                    rang += 1
            elif argument.startswith("-") and len(argument) > 1:
                for position, lettre in enumerate(argument[1:], start=1):
                    if lettre == "n":
                        raise refuser("git commit -n", REGLE_PRECOMMIT)
                    if lettre in "mF":
                        avec_message = True
                    if lettre in "mFCct":
                        if position == len(argument) - 1:
                            rang += 1
                        break
                    if lettre in "Su":
                        break
            rang += 1
        if not avec_message:
            raise refuser("git commit sans -m ni -F", REGLE_DOUTE)
        if not self.etat.hook_precommit_present():
            raise refuser(
                "hook pre-commit absent ou inactif (dossier hooks commun du dépôt, "
                "ou core.hooksPath défini)",
                REGLE_PRECOMMIT,
            )

    def push(self, arguments: list[str], surcharge: bool, ailleurs: bool) -> None:
        positionnels: list[str] = []
        rang = 0
        while rang < len(arguments):
            argument = arguments[rang]
            if argument == "--":
                positionnels += arguments[rang + 1 :]
                break
            if argument.startswith("--"):
                nom = argument.split("=", 1)[0]
                if nom in PUSH_INTERDITS:
                    raise refuser(f"git push {nom}", REGLE_PUSH)
                if nom not in PUSH_PERMIS:
                    raise refuser(f"option « {nom} » de git push inconnue", REGLE_DOUTE)
                if nom in PUSH_AVEC_VALEUR and "=" not in argument:
                    rang += 1
            elif argument.startswith("-") and len(argument) > 1:
                for position, lettre in enumerate(argument[1:], start=1):
                    if lettre in "fd":
                        raise refuser(f"git push -{lettre}", REGLE_PUSH)
                    if lettre == "o":
                        if position == len(argument) - 1:
                            rang += 1
                        break
                    if lettre not in "uqvn46":
                        raise refuser(f"option « -{lettre} » de git push inconnue", REGLE_DOUTE)
            else:
                positionnels.append(argument)
            rang += 1
        if surcharge:
            raise refuser("git -c avec git push", REGLE_DOUTE)
        etat_local = not (ailleurs or self.depot_ailleurs)
        refspecs = positionnels[1:]
        if not refspecs:
            if not etat_local:
                raise refuser("git push hors du dossier courant", REGLE_DOUTE)
            if self.etat.config_push_risquee():
                raise refuser("push.default ou remote.*.push réglé", REGLE_DOUTE)
            if est_main(self.etat.branche_courante()):
                raise refuser("git push depuis la branche main", REGLE_PUSH)
            amont = self.etat.amont()
            if amont is not None and est_main(amont.split("/", 1)[-1]):
                raise refuser("git push vers la branche suivie main", REGLE_PUSH)
            return
        for refspec in refspecs:
            if refspec.startswith("+"):
                raise refuser("git push forcé (+)", REGLE_PUSH)
            if "*" in refspec:
                raise refuser("git push avec un motif", REGLE_DOUTE)
            source, separateur, destination = refspec.partition(":")
            cible = destination if separateur else source
            if separateur and destination in {"", "HEAD", "@"}:
                raise refuser(f"destination de git push « {refspec} »", REGLE_DOUTE)
            if cible in {"HEAD", "@"}:
                if not etat_local:
                    raise refuser("git push HEAD hors du dossier courant", REGLE_DOUTE)
                cible = self.etat.branche_courante()
            if cible.startswith("refs/"):
                if cible.startswith("refs/heads/"):
                    cible = cible[len("refs/heads/") :]
                elif not cible.startswith("refs/tags/"):
                    raise refuser(f"destination de git push « {cible} »", REGLE_DOUTE)
            if est_main(cible) or (separateur and source == ""):
                raise refuser(f"git push vers « {refspec} »", REGLE_PUSH)


def sauter_depot(arguments: list[str]) -> list[str]:
    rang = 0
    while rang < len(arguments):
        if arguments[rang] in {"-R", "--repo"}:
            rang += 2
        elif arguments[rang].startswith("--repo="):
            rang += 1
        else:
            break
    return arguments[rang:]


def valeur(arguments: list[str], rang: int) -> str:
    if rang + 1 >= len(arguments):
        raise refuser(f"option « {arguments[rang]} » sans valeur", REGLE_DOUTE)
    return arguments[rang + 1]


def verifier_retrait_etiquette(options: list[str]) -> None:
    for rang, option in enumerate(options):
        retrait = None
        if option == "--remove-label":
            retrait = valeur(options, rang)
        elif option.startswith("--remove-label="):
            retrait = option.split("=", 1)[1]
        if retrait is not None and ETIQUETTE in retrait:
            raise refuser("retrait de l'étiquette du garde", REGLE_REGLAGES)


def verifier_creation_pr(options: list[str]) -> None:
    noms = {option.split("=", 1)[0] for option in options}
    if noms & {"-b", "--body", "-f", "--fill", "--fill-first", "--fill-verbose"}:
        raise refuser("gh pr create sans --body-file", REGLE_DOUTE)
    if not noms & {"-F", "--body-file"}:
        raise refuser("gh pr create sans --body-file", REGLE_DOUTE)


def regle_ecriture(route: str) -> str:
    return REGLE_FUSION if "merge" in route.lower() else REGLE_REGLAGES


def est_main(nom: str) -> bool:
    return nom.strip().lower() == "main"


# --- Amorçage ---------------------------------------------------------------------------------


def amorcage(commande: str, dossier: Path | None, etat: Etat) -> None:
    if dossier is None or dossier.resolve() != RACINE:
        raise refuser("commande d'amorçage hors de la racine du projet", REGLE_DOUTE)
    if commande == AMORCAGE_SECURITE:
        if etat.lire_json(".github/securite-depot.json") != REFERENCE_SECURITE:
            raise refuser(".github/securite-depot.json diffère de la référence", REGLE_REGLAGES)
        statut = etat.statut_blocage_secrets()
        if statut is None:
            raise refuser("blocage des secrets non proposé par GitHub", REGLE_REGLAGES)
        if statut == "enabled":
            raise refuser("blocage des secrets déjà actif : exception refermée", REGLE_REGLAGES)
    elif commande == AMORCAGE_PUSH:
        if not etat.main_distante_absente():
            raise refuser("main existe déjà sur GitHub : exception refermée", REGLE_PUSH)
    else:
        if etat.lire_json(".github/protection-main.json") != REFERENCE_PROTECTION:
            raise refuser(".github/protection-main.json diffère de la référence", REGLE_REGLAGES)
        if not etat.protection_absente():
            raise refuser("main est déjà protégée : exception refermée", REGLE_REGLAGES)


def analyser(commande: str, dossier: Path | None, etat: Etat) -> None:
    if commande in {AMORCAGE_SECURITE, AMORCAGE_PUSH, AMORCAGE_PROTECTION}:
        amorcage(commande, dossier, etat)
        return
    chercher_motifs_bruts(commande)
    ailleurs, configuration = False, False
    if re.search(r"\b(?:git|gh)\b|git-", commande):
        ailleurs, configuration = contexte(commande, 0)
    Analyse(etat, ailleurs, configuration).texte(commande, 0)


def principal(texte: str, fabrique: Callable[[Path], Etat]) -> int:
    try:
        donnees = json.loads(texte)
        if not isinstance(donnees, dict) or donnees.get("tool_name") != "Bash":
            raise refuser("entrée inattendue", REGLE_DOUTE)
        entree = donnees.get("tool_input")
        commande = entree.get("command") if isinstance(entree, dict) else None
        if not isinstance(commande, str):
            raise refuser("commande absente", REGLE_DOUTE)
        cwd = donnees.get("cwd")
        dossier = Path(cwd) if isinstance(cwd, str) and cwd else None
        analyser(commande, dossier, fabrique(dossier or RACINE))
    except Refus as refus:
        print(f"Refusé par le hook Claude Code : {refus}.", file=sys.stderr)
        return 2
    except Exception as erreur:
        print(
            f"Refusé par le hook Claude Code : erreur interne ({type(erreur).__name__}) "
            f"({REGLE_DOUTE}).",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    try:
        code = principal(sys.stdin.read(), Etat)
    except BaseException:
        print(f"Refusé par le hook Claude Code : erreur interne ({REGLE_DOUTE}).", file=sys.stderr)
        code = 2
    sys.exit(code)
