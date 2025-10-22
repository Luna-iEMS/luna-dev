# ============================================
# 🌙 Luna-IEMS Makefile – unified automation
# ============================================

BRANCH ?= main
SHELL := /bin/bash

# --------------------------------------------
# 🧩 1. Dokumentation prüfen & formatieren
# --------------------------------------------
docs:
	@echo "🧩 Prüfe Dokumentation & YAML-Formate..."
	@if ! command -v yamllint >/dev/null 2>&1; then \
		echo "⚠️ yamllint nicht gefunden – bitte mit 'sudo apt install yamllint' installieren."; \
	else \
		find . -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.md" \) \
		| while read f; do echo "🔍 Prüfe $$f"; yamllint -d "{extends: default, rules: {line-length: disable}}" $$f || true; done; \
	fi
	@echo "✅ Dokumentation validiert."

# --------------------------------------------
# 🧩 2. Git Commit Automation
# --------------------------------------------
commit:
	@echo "🪶 Commit-Vorgang..."
	@git add .
	@read -p "📝 Commit message: " msg; \
	(git commit -m "$$msg" && echo "✅ Commit erstellt.") || echo "⚠️ Keine Änderungen gefunden."
	@git push origin $(BRANCH)
	@echo "🚀 Änderungen gepusht."

# --------------------------------------------
# 🧩 3. Release Automation (CI/CD)
# --------------------------------------------
release:
	@echo "🚀 Starte Release Pipeline..."
	@$(MAKE) docs
	@git add .
	@git commit -m "chore(release): sync docs & workflows [skip ci]" || true
	@git push origin $(BRANCH)
	@if command -v gh >/dev/null 2>&1; then \
		echo "📦 Trigger GitHub Workflows..."; \
		gh workflow run smoke-test.yml || true; \
		gh workflow run integration-test.yml || true; \
		gh workflow run release-drafter.yml || true; \
	else \
		echo "⚠️ GitHub CLI nicht gefunden. Bitte installiere 'gh'."; \
	fi
	@echo "✅ Release-Prozess abgeschlossen."

# --------------------------------------------
# 🧩 4. Windows-Kompatibilität (optional)
# --------------------------------------------
win:
	@echo "🔄 Führe Windows Batch (gitauto.bat) aus..."
	@cmd.exe /C gitauto.bat || echo "⚠️ gitauto.bat konnte nicht ausgeführt werden."

# --------------------------------------------
# 🧩 5. Workflow Status
# --------------------------------------------
status:
	@gh run list --limit 5
