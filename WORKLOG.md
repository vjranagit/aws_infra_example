### 2025-08-31T03:27:53Z

**Actions**

* Enabled Playwright debug mode by default in run-docker.sh and boot-strap.sh.
* Added PWDEBUG and PWDEBUG_PORT to .env.example and updated README.

**Results**

* bash -n infra/init/boot-strap.sh
* bash -n infra/init/job-auto-apply/run-docker.sh
* python3 -m py_compile infra/init/job-auto-apply/job_apply.py
* yamllint infra/init/job-auto-apply/form_selectors.yml
* terraform fmt -check infra/instance.tf (command not found)

**Commits**

*

**Next**

* Monitor inspector output and refine automation as needed.

**Commit**

* 50eef89e6d1ad7bc0785e52489aca7f912c6e917
* 4142e367f51e7f2ae20f0b27a80f8b7de81702a3
* 2279d1315b4a566b504c1a369366af2d4f16780d
