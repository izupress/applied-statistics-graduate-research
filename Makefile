.PHONY: manifest chapter21 audit coordinate

manifest:
	python code/Python/generate_chapter_manifest.py

chapter21:
	python code/Python/chapter21_audit_workflows.py

audit:
	python code/Python/run_reproducibility_audit.py

coordinate: manifest chapter21 audit

