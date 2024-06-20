SCRIPTS_DIR := ./scripts
SCRIPTS := $(wildcard $(SCRIPTS_DIR)/*.sh)
SCRIPT_NAMES := $(notdir $(basename $(SCRIPTS)))
SCRIPTS_WITH_ARG := add remove

.PHONY: default
default:
	@echo "[make] $(SCRIPT_NAMES)"

.PHONY: $(SCRIPT_NAMES)
$(SCRIPT_NAMES): %: $(SCRIPTS_DIR)/%.sh
	@echo "[make] $@"
	@if echo "$(SCRIPTS_WITH_ARG)" | grep -qw "$@"; then \
		if [ "$(word 2,$(MAKECMDGOALS))" = "" ]; then \
			echo "[make] Error: argument is required for $@"; \
			exit 1; \
		fi; \
		arg=$(word 2,$(MAKECMDGOALS)); \
		bash $< $$arg; \
	else \
		bash $<; \
	fi

# Ignore the second argument to prevent Make from thinking it is a target
%:
	@:

.PHONY: all
all: $(SCRIPT_NAMES)

