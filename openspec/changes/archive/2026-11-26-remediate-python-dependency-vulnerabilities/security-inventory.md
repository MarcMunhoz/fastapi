# Dependency security inventory

[Issue #12](https://github.com/MarcMunhoz/fastapi/issues/12) tracks this maintenance round. The baseline checkout is `8f278c7`, with `app/poetry.lock` SHA-256 `45f8652df9c0582a63e7f40b9cd08a5d3750b08e3cd8e077433b4d2d9f677bc8`.

## Dependabot baseline

All 14 open alerts refer to `app/poetry.lock`.

| Alert | Advisory | Severity | Package | GitHub scope | First patched |
| --- | --- | --- | --- | --- | --- |
| #26 | CVE-2026-112909 | medium | `filelock` | runtime | `4.2.1` |
| #25 | CVE-2026-112910 | medium | `filelock` | runtime | `4.2.1` |
| #24 | CVE-2026-112915 | medium | `filelock` | runtime | `4.2.1` |
| #23 | CVE-2026-112936 | medium | `filelock` | runtime | `4.0.9` |
| #22 | CVE-2026-112939 | medium | `filelock` | runtime | `4.2.1` |
| #21 | CVE-2026-112935 | medium | `filelock` | runtime | `4.2.1` |
| #20 | GHSA-6q48-6c7w-9gw2 | critical | `certifi` | runtime | `2026.10.18` |
| #19 | CVE-2026-114613 | high | `msgpack` | runtime | `1.2.3` |
| #18 | CVE-2026-112913 | low | `filelock` | development | `4.2.1` |
| #17 | CVE-2026-112907 | low | `filelock` | development | `4.2.1` |
| #16 | CVE-2026-112940 | high | `filelock` | development | `4.2.1` |
| #15 | CVE-2026-97689 | high | `urllib3` | development | `2.8.0` |
| #13 | CVE-2026-97687 | high | `urllib3` | development | `2.8.0` |
| #12 | CVE-2026-97688 | medium | `urllib3` | development | `2.8.0` |

Poetry places all four packages in the development group. The baseline lockfile resolves `pip-audit → requests → certifi 2026.5.20 / urllib3 2.7.0` and `pip-audit → cachecontrol[filecache] → filelock 3.29.0 / msgpack 1.2.2`.

## Audit and resolution

The baseline development audit examined 52 distributions. It returned 15 records for the 14 Dependabot advisories. Both certifi records are `PYSEC-2026-4320`, aliased to `GHSA-6q48-6c7w-9gw2`. The urllib3 audit records `PYSEC-2026-4177`, `PYSEC-2026-4176`, and `PYSEC-2026-4175` map to alerts #15, #12, and #13 respectively.

| Package | Baseline | Final |
| --- | --- | --- |
| certifi | 2026.5.20 | 2026.11.20 |
| filelock | 3.29.0 | 4.3.1 |
| msgpack | 1.2.2 | 1.2.4 |
| urllib3 | 2.7.0 | 2.8.0 |
| pip-audit | 2.10.0 | 2.10.1 |
| pytest | 9.0.3 | 9.2.0 |
| Ruff | 0.15.15 | 0.15.22 |

The existing CacheControl constraint admits filelock 4.x, and its file-backed audit cache worked in the final container. FastAPI, Uvicorn, and pytest-cov retained their locked versions after targeted resolution within the existing direct constraints. The final lockfile SHA-256 is `c737c30ef7a6625e7c8df891c5ec797ef25125e022bec201bda407b12533ec1e`.

The final development audit examined 52 distributions and returned zero findings. Poetry verified the lockfile with existing deprecation warnings. Ruff lint and format checks passed. The project contains no collected repository tests, so pytest ran two temporary HTTP regression cases for `/` and `/health`, both of which passed.

## Production image

The initial production inventory excluded all four affected dependencies and the development audit and test tools. It revealed a separate image dependency: `pip 25.0.1` inherited from the Python base image. Auditing the installed versions reported 12 records for six distinct advisories: `PYSEC-2026-1795`, `PYSEC-2026-1796`, `PYSEC-2026-2875`, `PYSEC-2026-2876`, `PYSEC-2026-196`, and `PYSEC-2026-3721`.

The production stage now upgrades this installed copy to `26.2.1` using the version and distribution hashes already recorded in the Poetry lockfile. Applying the upgrade after copying the runtime dependencies replaces the inherited pip distribution and its metadata.

The rebuilt production image contains 20 installed distributions, including exactly one `pip 26.2.1`. It excludes certifi, filelock, msgpack, urllib3, pip-audit, Ruff, and pytest. The audit of the exact installed versions returned zero findings. Both `/` and `/health` returned HTTP 200 with the expected JSON from that image.

The base image still contains the upstream `ensurepip` bootstrap wheel for `pip 25.0.1`. It is outside the installed package audit and is not used by the service. A bootstrap that uses that bundled wheel, such as creating a new virtual environment in the production image, can reintroduce the affected version. The production build and service startup use the verified installed copy. Removing or replacing the upstream bootstrap wheel would change the base image's virtual environment behavior.
