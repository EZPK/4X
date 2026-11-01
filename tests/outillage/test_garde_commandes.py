"""Tests du hook `.claude/hooks/garde_commandes.py` (plan détaillé, points 26 et 34).

L'état de GitHub et du dépôt local est simulé par une fausse `Etat` : aucun appel réseau.
"""

import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

RACINE = Path(__file__).resolve().parents[2]
HOOK = ".claude/hooks/garde_commandes.py"
AMORCAGE_SECURITE = "gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json"
AMORCAGE_PUSH = "git push -u origin main"
AMORCAGE_PROTECTION = (
    "gh api -X PUT repos/EZPK/4X/branches/main/protection --input .github/protection-main.json"
)


@pytest.fixture(scope="module")
def hook() -> ModuleType:
    spec = importlib.util.spec_from_file_location("garde_commandes", RACINE / HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Reglages:
    """Ce que répond la fausse `Etat`. Une exception simule une lecture en échec."""

    def __init__(self, **valeurs: Any) -> None:
        self.statut: str | None | Exception = "disabled"
        self.main_absente: bool | Exception = True
        self.protection_absente: bool | Exception = True
        self.depot_existe: bool | Exception = False
        self.hook_present: bool | Exception = True
        self.branche: str | Exception = "essai/x"
        self.amont: str | None = "origin/essai/x"
        self.config_risquee = False
        self.fichiers: dict[str, object] = {}
        self.__dict__.update(valeurs)


@pytest.fixture
def lancer(hook: ModuleType) -> Callable[..., int]:
    def lancer(
        commande: str,
        reglages: Reglages | None = None,
        cwd: str | None = str(RACINE),
    ) -> int:
        r = reglages or Reglages()

        def rendre(valeur: Any) -> Any:
            if isinstance(valeur, Exception):
                raise valeur
            return valeur

        class FausseEtat(hook.Etat):  # type: ignore[name-defined, misc]
            def lancer(self, *commande: str) -> subprocess.CompletedProcess[str]:
                raise AssertionError(f"commande réelle lancée : {commande}")

            def lire_json(self, relatif: str) -> object:
                if relatif in r.fichiers:
                    return r.fichiers[relatif]
                return super().lire_json(relatif)

            def statut_blocage_secrets(self) -> str | None:
                return rendre(r.statut)  # type: ignore[no-any-return]

            def main_distante_absente(self) -> bool:
                return rendre(r.main_absente)  # type: ignore[no-any-return]

            def protection_absente(self) -> bool:
                return rendre(r.protection_absente)  # type: ignore[no-any-return]

            def depot_existe(self) -> bool:
                return rendre(r.depot_existe)  # type: ignore[no-any-return]

            def hook_precommit_present(self) -> bool:
                return rendre(r.hook_present)  # type: ignore[no-any-return]

            def branche_courante(self) -> str:
                return rendre(r.branche)  # type: ignore[no-any-return]

            def amont(self) -> str | None:
                return r.amont

            def config_push_risquee(self) -> bool:
                return r.config_risquee

        entree: dict[str, Any] = {"tool_name": "Bash", "tool_input": {"command": commande}}
        if cwd is not None:
            entree["cwd"] = cwd
        return int(hook.principal(json.dumps(entree), FausseEtat))

    return lancer


def refuse(lancer: Callable[..., int], commande: str, **reglages: Any) -> None:
    assert lancer(commande, Reglages(**reglages)) == 2, commande


def passe(lancer: Callable[..., int], commande: str, **reglages: Any) -> None:
    assert lancer(commande, Reglages(**reglages)) == 0, commande


# --- Fusion ---


@pytest.mark.parametrize(
    "commande",
    [
        "gh pr merge 1",
        "gh pr merge 1 --admin",
        "gh pr merge --auto --squash 1",
        "gh  pr   merge 1",
        "gh -R EZPK/4X pr merge 1",
        "gh pr -R EZPK/4X merge 1",
        "ls && gh pr merge 1",
        "ls; gh pr merge 1",
        "ls || gh pr merge 1",
        "echo 1 | gh pr merge 1",
        "x=$(gh pr merge 1)",
        "(gh pr merge 1)",
        "bash -c 'gh pr merge 1'",
        'eval "gh pr merge 1"',
        "/usr/bin/gh pr merge 1",
        "ls\ngh pr merge 1",
        "gh api -X PUT repos/EZPK/4X/pulls/1/merge",
        "gh api --method PUT repos/EZPK/4X/pulls/1/merge -f merge_method=squash",
    ],
)
def test_fusion_refusee(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


# --- Push ---


@pytest.mark.parametrize(
    "commande",
    [
        "git push origin main",
        "git push origin HEAD:main",
        "git push origin x:refs/heads/main",
        "git push origin :main",
        "git push origin refs/heads/main",
        "git push origin MAIN",
        "git push --force origin essai/x",
        "git push -f origin essai/x",
        "git push -uf origin essai/x",
        "git push --force-with-lease origin essai/x",
        "git push --force-with-lease=essai/x origin essai/x",
        "git push --mirror origin",
        "git push --all origin",
        "git push --delete origin essai/x",
        "git push -d origin essai/x",
        "git push --prune origin",
        "git push origin +essai/x",
        "git push origin 'refs/heads/*:refs/heads/*'",
        "git push origin :essai/x",
        "git push origin essai/x:",
        "git push origin refs/pull/1/head",
        "git -c remote.origin.push=refs/heads/x:refs/heads/main push",
        "git -C ailleurs push",
        "cd ailleurs && git push",
        "git push --inconnue origin essai/x",
        "git push -z origin essai/x",
        "ls && git push origin main",
        "bash -c 'git push origin main'",
        "git push -u origin main ",
        "git push -u origin main && ls",
    ],
)
def test_push_refuse(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


def test_push_depuis_main_refuse(lancer: Callable[..., int]) -> None:
    refuse(lancer, "git push", branche="main", amont="origin/main")
    refuse(lancer, "git push origin", branche="main", amont=None)
    refuse(lancer, "git push origin HEAD", branche="main")
    refuse(lancer, "git push origin @", branche="main")


def test_push_vers_la_branche_suivie_main_refuse(lancer: Callable[..., int]) -> None:
    refuse(lancer, "git push", branche="essai/x", amont="origin/main")


def test_push_avec_config_risquee_refuse(lancer: Callable[..., int]) -> None:
    refuse(lancer, "git push", config_risquee=True)


def test_push_branche_courante_illisible_refuse(
    lancer: Callable[..., int], hook: ModuleType
) -> None:
    refuse(lancer, "git push", branche=hook.ErreurLecture("détachée"))


@pytest.mark.parametrize(
    "commande",
    [
        "git push",
        "git push -u origin essai/x",
        "git push --set-upstream origin essai/x",
        "git push origin HEAD",
        "git push origin essai/x:essai/x",
        "git push origin HEAD:refs/heads/essai/x",
        "git push -o ci.skip origin essai/x",
        "git push --dry-run origin essai/x",
        "git push origin v0.1",
        "git push origin refs/tags/v0.1",
    ],
)
def test_push_permis(lancer: Callable[..., int], commande: str) -> None:
    passe(lancer, commande)


# --- Contournement du hook pre-commit ---


@pytest.mark.parametrize(
    "commande",
    [
        "git commit --no-verify -m x",
        "git push --no-verify origin essai/x",
        "git commit -n -m x",
        "git commit -nm x",
        "git commit -an -m x",
        "git commit -n --allow-empty --dry-run -m test",
        "SKIP=gitleaks git commit -m x",
        "env SKIP=gitleaks git commit -m x",
        "git -c core.hooksPath=/dev/null commit -m x",
        "git config core.hooksPath /tmp/vide",
        "git config CORE.HOOKSPATH /tmp/vide",
        "pre-commit uninstall",
        "uv run pre-commit uninstall",
        "git commit",
        "git commit -a",
        "git commit -C HEAD",
        "git -C ailleurs commit -m x",
        "cd ailleurs && git commit -m x",
    ],
)
def test_contournement_refuse(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


def test_commit_sans_hook_pre_commit_refuse(lancer: Callable[..., int], hook: ModuleType) -> None:
    refuse(lancer, "git commit -m x", hook_present=False)
    refuse(lancer, "git commit -F message.txt", hook_present=hook.ErreurLecture("pas de .git"))


@pytest.mark.parametrize(
    "commande",
    [
        "git commit -m x",
        "git commit -am x",
        "git commit -m 'deux mots'",
        "git commit --message=x",
        "git commit --message x",
        "git commit -F message.txt",
        "git commit --file=message.txt",
        "git commit -uno -m x",
        "git commit --author 'A <a@b.c>' -m x",
        "git commit --amend -m x",
    ],
)
def test_commit_permis(lancer: Callable[..., int], commande: str) -> None:
    passe(lancer, commande)


# --- Réglages et écritures sur GitHub ---


@pytest.mark.parametrize(
    "commande",
    [
        "gh repo edit --visibility private",
        "gh repo delete EZPK/4X --yes",
        "gh repo archive EZPK/4X",
        "gh repo rename autre",
        "gh repo set-default EZPK/4X",
        "gh api -X PATCH repos/EZPK/4X -f private=true",
        "gh api -X PATCH repos/EZPK/4X --input .github/securite-depot.json --silent",
        "gh api -X PUT repos/EZPK/4X/branches/main/protection --input autre.json",
        "gh api -X DELETE repos/EZPK/4X/branches/main/protection",
        "gh api -X POST repos/EZPK/4X/rulesets --input r.json",
        "gh api repos/EZPK/4X/actions/permissions/workflow -X PUT"
        " -f default_workflow_permissions=write",
        "gh api graphql -f query='mutation { x }'",
        "gh api graphql -f query='{ viewer { login } }'",
        "gh api --method=DELETE repos/EZPK/4X/git/refs/heads/main",
        "gh api -X DELETE repos/EZPK/4X/git/refs/heads/essai/../main",
        "gh api -X DELETE repos/EZPK/4X/git/refs/heads/autre",
        "gh api -XPATCH repos/EZPK/4X/pulls/1 -f base=main",
        "gh api -X PATCH repos/EZPK/4X/pulls/1 -f state=open",
        "gh api -X PATCH repos/EZPK/4X/pulls/1 --input corps.json",
        "gh api -X PATCH repos/EZPK/4X/issues/1 -f 'labels[]=autre'",
        "gh api -X DELETE 'repos/EZPK/4X/issues/1/labels/fichiers%20prot%C3%A9g%C3%A9s'",
        "gh api -X PUT repos/EZPK/4X/issues/1/labels -f 'labels[]=autre'",
        "gh api -X DELETE repos/EZPK/4X/labels/x",
        "gh api -X POST repos/EZPK/autre/issues -f title=x",
        "gh api -X POST repos/{owner}/{repo}/issues -f title=x",
        "gh api -X POST repos/EZPK/4X/pulls/1/reviews -f event=APPROVE",
        "gh api user/repos -f name=x",
        "gh api -f title=x repos/EZPK/4X/hooks",
        "gh api -X GET search/issues -f q=x",
        "gh api --inconnue repos/EZPK/4X",
        "gh api repos/EZPK/4X repos/EZPK/autre",
        "gh api -X",
        "gh secret set X",
        "gh variable set X",
        "gh alias set m 'pr merge'",
        "gh extension install x/y",
        "gh workflow run ci.yml",
        "gh workflow disable ci.yml",
        "gh run rerun 5",
        "gh auth token",
        "gh auth refresh -s admin:org",
        "gh label delete x",
        "gh label edit 'fichiers protégés modifiés' --name autre",
        "gh pr close 1",
        "gh pr review 1 --approve",
        "gh pr ready 1",
        "gh issue delete 1",
        "gh release create v1",
        "gh inconnue",
    ],
)
def test_ecriture_refusee(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


@pytest.mark.parametrize(
    "commande",
    [
        "gh api repos/EZPK/4X",
        "gh api repos/EZPK/4X/branches/main/protection",
        "gh api -X GET repos/EZPK/4X/pulls",
        "gh api --paginate repos/EZPK/4X/pulls/1/files --jq '.[] | {filename, previous_filename}'",
        "gh api -H 'Accept: application/vnd.github.raw+json' repos/EZPK/4X/contents/a?ref=main",
        "gh api repos/gitleaks/gitleaks/commits/v8.30.1 --jq .sha",
        "gh api -X POST repos/EZPK/4X/labels -f name=x -f color=d93f0b -f description=y",
        "gh api -X POST repos/EZPK/4X/milestones -f title=M0 -f description=x",
        "gh api -X PATCH repos/EZPK/4X/milestones/1 -f state=closed",
        "gh api -X POST repos/EZPK/4X/issues -f title=x -f body=y",
        "gh api -X PATCH repos/EZPK/4X/issues/1 -f state=closed",
        "gh api -X POST repos/EZPK/4X/issues/1/comments -f body=x",
        "gh api -X POST repos/EZPK/4X/issues/1/labels -f 'labels[]=x'",
        "gh api -X PATCH repos/EZPK/4X/issues/comments/9 -f body=x",
        "gh api -X POST repos/EZPK/4X/pulls -f title=x -f head=essai/x -f base=main",
        "gh api -X PATCH repos/EZPK/4X/pulls/3 -f state=closed",
        "gh api -X PATCH repos/EZPK/4X/pulls/3 -F body=@corps.md",
        "gh api -X POST repos/EZPK/4X/pulls/3/comments -f body=x",
        "gh api -X DELETE repos/EZPK/4X/git/refs/heads/essai/x",
        "gh api -X DELETE /repos/ezpk/4x/git/refs/heads/essai/a/b",
        "gh pr view 1",
        "gh pr list",
        "gh pr checks 1",
        "gh pr diff 1",
        "gh pr comment 1 --body-file c.md",
        "gh pr create --title t --body-file b.md --base main --head essai/x",
        "gh pr create -F b.md -t t",
        "gh pr edit 1 --add-label x",
        "gh pr edit 1 --remove-label autre",
        "gh issue view 1",
        "gh run list",
        "gh run view 5 --log",
        "gh repo view EZPK/4X",
        "gh release download v8.30.1 -R gitleaks/gitleaks",
        "gh auth status",
        "gh --version",
        "gh",
        "ls",
        "uv run pytest -q",
        "cat a | grep b > c",
        "gitleaks git --pre-commit --staged --redact --config .gitleaks.toml .",
        "git status --short",
        "git diff --cached",
        "git log --format=%B -1",
        "git --version",
        "echo 'texte non fermé",
    ],
)
def test_commande_permise(lancer: Callable[..., int], commande: str) -> None:
    passe(lancer, commande)


@pytest.mark.parametrize(
    "commande",
    [
        "gh pr create --title t --body x",
        "gh pr create --fill",
        "gh pr create -f",
        "gh pr create --title t",
        "gh pr create --body-file b.md --body x",
    ],
)
def test_pr_create_sans_body_file_refuse(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


@pytest.mark.parametrize(
    "commande",
    [
        "gh pr edit 1 --remove-label 'fichiers protégés modifiés'",
        "gh pr edit 1 --remove-label=autre,'fichiers protégés modifiés'",
        "gh issue edit 1 --remove-label 'fichiers protégés modifiés'",
    ],
)
def test_retrait_etiquette_du_garde_refuse(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


def test_creation_du_depot(lancer: Callable[..., int], hook: ModuleType) -> None:
    commande = "gh repo create EZPK/4X --public --source ."
    passe(lancer, commande, depot_existe=False)
    refuse(lancer, commande, depot_existe=True)
    refuse(lancer, commande, depot_existe=hook.ErreurLecture("réseau"))
    refuse(lancer, commande + " --push", depot_existe=False)
    refuse(lancer, "gh repo create EZPK/autre --public", depot_existe=False)
    refuse(lancer, "gh repo create --public", depot_existe=False)


# --- Amorçage : quatre états simulés ---


def test_amorcage_securite(lancer: Callable[..., int], hook: ModuleType) -> None:
    passe(lancer, AMORCAGE_SECURITE, statut="disabled")
    refuse(lancer, AMORCAGE_SECURITE, statut="enabled")
    refuse(lancer, AMORCAGE_SECURITE, statut=None)
    refuse(lancer, AMORCAGE_SECURITE, statut=hook.ErreurLecture("réseau"))
    modifie = {"security_and_analysis": {"secret_scanning": {"status": "enabled"}}}
    refuse(
        lancer,
        AMORCAGE_SECURITE,
        statut="disabled",
        fichiers={".github/securite-depot.json": modifie},
    )


def test_amorcage_push(lancer: Callable[..., int], hook: ModuleType) -> None:
    passe(lancer, AMORCAGE_PUSH, main_absente=True)
    refuse(lancer, AMORCAGE_PUSH, main_absente=False)
    refuse(lancer, AMORCAGE_PUSH, main_absente=hook.ErreurLecture("réseau"))


def test_amorcage_protection(lancer: Callable[..., int], hook: ModuleType) -> None:
    passe(lancer, AMORCAGE_PROTECTION, protection_absente=True)
    refuse(lancer, AMORCAGE_PROTECTION, protection_absente=False)
    refuse(lancer, AMORCAGE_PROTECTION, protection_absente=hook.ErreurLecture("404 autre"))
    modifie = dict(hook.REFERENCE_PROTECTION, enforce_admins=False)
    refuse(
        lancer,
        AMORCAGE_PROTECTION,
        protection_absente=True,
        fichiers={".github/protection-main.json": modifie},
    )


@pytest.mark.parametrize("commande", [AMORCAGE_SECURITE, AMORCAGE_PUSH, AMORCAGE_PROTECTION])
def test_amorcage_hors_de_la_racine(
    lancer: Callable[..., int], commande: str, tmp_path: Path
) -> None:
    assert lancer(commande, Reglages(), str(tmp_path)) == 2
    assert lancer(commande, Reglages(), None) == 2


def test_copies_de_reference_egales_aux_fichiers(hook: ModuleType) -> None:
    for nom, reference in (
        ("securite-depot.json", hook.REFERENCE_SECURITE),
        ("protection-main.json", hook.REFERENCE_PROTECTION),
    ):
        with open(RACINE / ".github" / nom, encoding="utf-8") as fichier:
            assert json.load(fichier) == reference, nom


# --- Erreur interne et analyse impossible ---


@pytest.mark.parametrize(
    "entree",
    [
        "pas du json",
        "[]",
        json.dumps({"tool_input": {"command": "ls"}}),
        json.dumps({"tool_name": "Edit", "tool_input": {"command": "ls"}}),
        json.dumps({"tool_name": "Bash", "tool_input": {}}),
        json.dumps({"tool_name": "Bash", "tool_input": {"command": 3}}),
        json.dumps({"tool_name": "Bash", "tool_input": "ls"}),
    ],
)
def test_entree_inattendue_refusee(hook: ModuleType, entree: str) -> None:
    assert hook.principal(entree, hook.Etat) == 2


def test_erreur_interne_refusee(hook: ModuleType, capsys: pytest.CaptureFixture[str]) -> None:
    class Cassee(hook.Etat):  # type: ignore[name-defined, misc]
        def branche_courante(self) -> str:
            raise RuntimeError("panne")

        def config_push_risquee(self) -> bool:
            return False

    entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push"}})
    assert hook.principal(entree, Cassee) == 2
    assert "erreur interne (RuntimeError)" in capsys.readouterr().err


@pytest.mark.parametrize("commande", ["git commit -m 'non fermé", 'gh pr view "1'])
def test_analyse_impossible_refusee(lancer: Callable[..., int], commande: str) -> None:
    refuse(lancer, commande)


def test_message_cite_la_regle(hook: ModuleType, capsys: pytest.CaptureFixture[str]) -> None:
    entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": "gh pr merge 1"}})
    assert hook.principal(entree, hook.Etat) == 2
    erreur = capsys.readouterr().err
    assert "Refusé par le hook Claude Code" in erreur
    assert "CLAUDE.md" in erreur


# --- Le script lancé comme par Claude Code (point 34) ---


@pytest.mark.parametrize(("commande", "attendu"), [("gh pr merge 1", 2), ("ls", 0)])
def test_script_reel(commande: str, attendu: int) -> None:
    entree = json.dumps({"tool_name": "Bash", "tool_input": {"command": commande}})
    resultat = subprocess.run(
        [sys.executable, "-I", str(RACINE / HOOK)],
        input=entree,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultat.returncode == attendu, resultat.stderr
