#!/bin/sh
# PreToolUse hook on Bash: before the agent opens a PR with gh, check two
# things and block with one message when either is missing.
#
#   1. `gh pr create` (or its alias `gh pr new`) carries --draft, unless
#      --web hands the PR to the browser.
#   2. A change that touches code also touches documentation, or the
#      command ends with the shell comment `# pr-gate: no-docs <reason>`.
#      gh never sees a comment, and the command still starts with gh, so
#      a permission rule such as Bash(gh pr create:*) keeps matching.
#
# Exit 2 blocks the call and hands stderr to the agent. It binds the agent
# only: a person can always run gh by hand. Anything this script cannot
# read or resolve passes with exit 0, so a missing remote or odd input
# never blocks anyone.
#
# Portable on purpose: POSIX sh, git, sed -E, grep -E, awk and tr only, and
# no path, account or repo name of any machine or project.
set -u

input=$(cat)
flat=$(printf '%s' "$input" | tr '\n' ' ')

# The Bash tool's command string, still JSON-escaped; enough to match on.
command=$(printf '%s' "$flat" \
  | sed -nE 's/.*"command"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p')
[ -n "$command" ] || exit 0

# Only a gh call that starts a shell segment counts, so text that merely
# mentions `gh pr create` (a commit message, an echo) passes.
segments=$(printf '%s\n' "$command" \
  | awk '{ gsub(/\\n|&&|\|\||;|\|/, "\n"); print }')
gh_line=$(printf '%s\n' "$segments" \
  | grep -E '^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*=[^[:space:]]*[[:space:]]+)*gh[[:space:]]+pr[[:space:]]+(create|new|ready)([[:space:]]|$)' \
  | head -n 1)
[ -n "$gh_line" ] || exit 0

# The verb right after `gh pr`, past any VAR=value prefixes; a title or
# body that says "ready" must not change it.
verb=$(printf '%s' "$gh_line" | tr -s ' \t' '  ' \
  | sed -E 's/^ ?([A-Za-z_][A-Za-z0-9_]*=[^ ]* )*//')
case "$verb" in
  "gh pr ready"*)
    action=ready
    # Back to draft is always fine.
    case "$command" in *"--undo"*) exit 0 ;; esac
    ;;
  *) action=create ;;
esac

# gh pointed at another repo: the local diff says nothing about it.
case " $command " in *" --repo"*|*" -R "*) skip_docs=1 ;; *) skip_docs=0 ;; esac

cwd=$(printf '%s' "$flat" \
  | sed -nE 's/.*"cwd"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' \
  | sed -e 's/\\\\/\\/g')
# `cd <dir> && gh pr ...` runs gh somewhere else: follow it.
target=$(printf '%s' "$command" \
  | sed -nE 's/^[[:space:]]*cd[[:space:]]+([^;&|[:space:]]+)[[:space:]]*&&.*/\1/p' \
  | sed -e 's/^\\"//' -e 's/\\"$//')
if [ -n "$target" ]; then
  case "$target" in
    /*|[A-Za-z]:*) cwd=$target ;;
    *) cwd="$cwd/$target" ;;
  esac
fi
[ -n "$cwd" ] && [ -d "$cwd" ] || exit 0
top=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || exit 0

missing=""

if [ "$action" = create ]; then
  case " $command " in
    # --web hands the PR to the browser, where the person decides.
    *" --draft"*|*" -d "*|*" --web"*|*" -w "*) ;;
    *) missing="$missing
- Open the PR as a draft: add --draft to gh pr create. The author marks it
  ready when it is."
      ;;
  esac
fi

docs_needed() {
  # The default branch of origin, then the usual names. None: pass.
  base=$(git -C "$top" symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null)
  if [ -z "$base" ]; then
    for b in origin/main origin/master; do
      if git -C "$top" rev-parse -q --verify "$b^{commit}" >/dev/null 2>&1; then
        base=$b
        break
      fi
    done
  fi
  [ -n "$base" ] || return 1
  mb=$(git -C "$top" merge-base "$base" HEAD 2>/dev/null) || return 1

  # Committed, staged, unstaged and untracked: the whole change.
  files=$( { git -C "$top" diff --name-only "$mb" 2>/dev/null; \
             git -C "$top" ls-files --others --exclude-standard 2>/dev/null; } )
  code=0
  docs=0
  for f in $files; do
    case "$f" in
      *.md|*.mdx|*.rst|*.adoc|*.txt|docs/*|*/docs/*|doc/*|*/doc/*|README*|*/README*|CHANGELOG*|*/CHANGELOG*)
        docs=1 ;;
      tests/*|*/tests/*|test/*|*/test/*|__tests__/*|*/__tests__/*|test_*|*/test_*|*_test.*|*.test.*|*.spec.*)
        ;;
      *.lock|*-lock.json|*-lock.yaml|*.lockb|go.sum|.gitignore|*/.gitignore|.github/*|.gitattributes)
        ;;
      *) code=1 ;;
    esac
  done
  [ "$code" = 1 ] && [ "$docs" = 0 ]
}

if [ "$skip_docs" = 0 ]; then
  case "$command" in
    *"# pr-gate: no-docs"*) ;;
    *)
      if docs_needed; then
        missing="$missing
- Red flag: this change touches code but no documentation (no *.md, docs/,
  README or CHANGELOG file changed). Update the docs the change affects;
  /docsjanitor can help. If no doc is affected, end the same command
  with the comment  # pr-gate: no-docs <reason>  and give the reason
  under Why in the PR body too."
      fi
      ;;
  esac
fi

[ -n "$missing" ] || exit 0
{
  echo "pr-gate: not yet. Before this PR in $(basename "$top"):$missing"
  echo "Fix these yourself and run the command again. Do not ask the user"
  echo "about git; explain the change in plain words if you ask anything."
} >&2
exit 2
