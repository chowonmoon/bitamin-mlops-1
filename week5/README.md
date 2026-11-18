# Week 5 — Docker + GitHub Actions CI/CD 실습

**목표:** 실제 고객 이탈 예측 API를 Docker 이미지로 만들고 push → 테스트 → 빌드 → Docker Hub 업로드를 연결합니다. 실습 50분. 원격 서버 자동 교체는 선택 확장입니다.

조별 기존 저장소에 [공통 출발 코드 가져오기](https://github.com/sumnunus/bitamin-mlops-week5-snapshot/blob/main/docs/IMPORT.md)를 먼저 완료하세요. 모든 명령은 **저장소 루트**에서 실행합니다. 루트의 이전 주차 Dockerfile·requirements.txt를 사용하지 않습니다.

## 역할 예시

| 담당 | 할 일 |
| --- | --- |
| A | API 테스트 작성 |
| B | Dockerfile 작성·컨테이너 실행 |
| C | Actions 작성·로그 확인 |
| D | 팀 Secrets·Docker Hub 준비·캡처·변경 통합 |

대표자가 변경을 작업 브랜치에 모으고 기본 브랜치에 병합합니다. 개인 토큰은 조원에게 채팅으로 공유하지 않고 대표자가 GitHub Secrets에 직접 등록합니다.

## STEP 0 — 환경과 API 확인 (5분)

Python 3.13.x, Git, Docker Desktop 실행 상태를 확인합니다. Windows는 **Linux containers**와 WSL 2 엔진을 사용합니다. Docker가 요구하는 사양을 충족하는 PC에서 진행하세요.

macOS:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r week5/requirements-dev.txt
python -m uvicorn week4.main:app --reload
```

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r week5/requirements-dev.txt
.\.venv\Scripts\python.exe -m uvicorn week4.main:app --reload
```

Windows에서 이후 `python` 명령은 **`.\.venv\Scripts\python.exe`로 바꾸어** 실행하세요. 가상환경을 활성화하지 않아도 되므로 PowerShell 실행 정책을 바꿀 필요가 없습니다. macOS의 새 터미널에서는 다시 `source .venv/bin/activate`를 실행합니다.

<http://127.0.0.1:8000/docs> → `POST /predict` → Try it out → Execute. 공통 모델로 예측 결과가 나오면 준비 완료입니다. Swagger 입력 예시는 이미 포함되어 있습니다. 별도 터미널에서 `python week5/smoke.py`로도 확인할 수 있습니다.

Docker 실습 전 로컬 Uvicorn 서버를 `Ctrl+C`로 종료해 8000 포트를 비웁니다.

## STEP 1 — API 테스트 작성 (10분)

`week5/test_main.py`의 `pytest.fail("TODO: ...")` 세 부분을 실제 검증으로 바꿉니다. TestClient는 HTTP 요청을 시뮬레이션하므로 별도 Uvicorn 서버를 띄울 필요가 없습니다.

첫 테스트 예시:

```python
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}
```

나머지 두 테스트를 작성하세요.

| 테스트 | 검증할 것 |
| --- | --- |
| `test_predict` | `client.post("/predict", json=SAMPLE)`이 200, `churn`이 정수 0/1, `churn_probability`가 0~1 |
| `test_missing_required_field` | `SAMPLE.copy()`에서 `tenure`를 제거한 요청이 422, 오류 위치에 `tenure` 포함 |

```bash
python -m pytest week5/test_main.py -v
```

**정상 결과: `3 passed`.** 출발 코드의 `3 failed`는 의도된 TODO입니다. `0 tests`·`skipped`는 통과가 아닙니다. 모델 예측 확률의 특정 소수점 값은 고정해 비교하지 않습니다.

## STEP 2 — Docker 이미지 빌드·실행 (10분)

`week5/Dockerfile`을 아래 순서로 완성합니다.

1. `FROM python:3.13-slim`
2. `WORKDIR /app`
3. `COPY week4/requirements.txt /app/requirements.txt`
4. `RUN python -m pip install --no-cache-dir -r /app/requirements.txt`
5. `COPY week4/ /app/week4/`
6. `EXPOSE 8000`
7. `CMD ["python", "-m", "uvicorn", "week4.main:app", "--host", "0.0.0.0", "--port", "8000"]`

`COPY`의 원본 경로는 **빌드 컨텍스트(명령 끝의 `.`)를 기준으로 한 상대 경로**입니다.

```bash
docker version
docker build -f week5/Dockerfile -t bitamin-mlops-week5:local .
docker run -d --name week5-api -p 8000:8000 bitamin-mlops-week5:local
python week5/smoke.py
docker logs week5-api
```

**정상 결과:** `PASS: / and /predict (real model inference)`와 예측 결과가 출력됩니다. <http://127.0.0.1:8000/docs>에서도 확인합니다.

```bash
docker rm -f week5-api
```

이 PC에서 만든 이미지는 이 PC의 CPU 아키텍처용입니다. STEP 4의 자동 업로드는 Intel/AMD용 `linux/amd64`와 Apple Silicon용 `linux/arm64`를 함께 만듭니다.

## STEP 3 — push 시 자동 테스트·빌드 (10분)

VS Code 등 편집기에서 `week5/templates/ci.yml.example`의 내용을 복사해 **루트 `.github/workflows/ci.yml`**로 저장합니다. 예시 파일 내용은 실행 가능한 테스트·빌드 워크플로이며, `needs: test`가 테스트 실패 시 빌드를 중단합니다.

```bash
git add week5/test_main.py week5/Dockerfile .github/workflows/ci.yml
git commit -m "Add API tests and Docker CI"
git push
```

자기 조 GitHub 저장소의 Actions → **Week 5 CI** → 방금 커밋을 선택합니다.

**정상 결과:** `test`와 `build` 성공. `build` 로그에는 컨테이너에서 실제 `/predict` 요청이 성공한 결과가 표시됩니다. GitHub 러너는 로컬 PC의 가상환경이나 Docker 이미지를 사용하지 않고 새 환경에서 검증합니다.

## STEP 4 — Docker Hub 자동 업로드 (10분)

1. 팀이 사용할 Docker Hub 계정에 공개 저장소 `bitamin-mlops-week5`를 만듭니다.
2. **자기 조 GitHub 저장소** Settings → Secrets and variables → Actions의 Secrets 탭에 다음을 등록합니다.

| Secret 이름 | 값 |
| --- | --- |
| `DOCKERHUB_USERNAME` | 팀이 사용할 Docker ID |
| `DOCKERHUB_TOKEN` | 그 계정의 Read & Write Personal Access Token |

3. Variables 탭에 `ENABLE_DOCKERHUB_PUSH` = `true`를 등록합니다. 이 값은 비밀이 아닙니다. 다른 이미지 이름을 쓰려면 `DOCKERHUB_IMAGE` Variable에 이름만 입력합니다.
4. `week5/templates/publish-job.yml.example` 내용을 `ci.yml` 맨 아래에 추가합니다. `publish:`는 `test:`·`build:`와 **같은 들여쓰기**이며 `jobs:` 아래에 속해야 합니다. 전체 정답은 `week5-final` 태그의 `ci.yml`에 있습니다.
5. 변경을 커밋·push하고 PR로 조별 저장소의 **기본 브랜치**에 병합합니다.

**정상 결과:** 기본 브랜치 실행에서 `test` → `build` → `publish` 모두 성공. Docker Hub Tags에 `latest`와 커밋 SHA 태그, `linux/amd64`·`linux/arm64`가 표시됩니다. `publish`는 업로드된 SHA 이미지도 다시 pull하여 API를 확인합니다.

작업 브랜치·PR 또는 Variable 미설정 상태에서는 `publish`가 **skipped**됩니다. 이것은 CP5 통과가 아닙니다. Secrets 등록 후에는 새 커밋을 push하거나 Actions → Week 5 CI → Run workflow에서 **기본 브랜치**를 선택합니다. 기본 브랜치 이름은 워크플로가 자동으로 읽으므로 `main`·`master` 모두 가능합니다.

### 업로드한 이미지로 실행 확인

아래 `YOUR_DOCKER_ID`를 실제 팀 Docker ID로 바꿉니다. Windows에서도 같은 Docker 명령을 사용합니다.

```bash
docker pull YOUR_DOCKER_ID/bitamin-mlops-week5:latest
docker run -d --name week5-hub -p 8000:8000 YOUR_DOCKER_ID/bitamin-mlops-week5:latest
python week5/smoke.py
docker rm -f week5-hub
```

원격 서버가 새 컨테이너로 자동 교체되는 단계는 이번 필수 실습에 포함하지 않습니다. 이번 자동화 범위는 테스트·이미지 빌드·레지스트리 전달입니다.

## 체크포인트·결과 제출 (마지막 5분)

각 조의 이 README 아래 결과 기록을 채우고, 화면은 `week5/captures/`에 저장합니다. 토큰 값·Secret 입력 화면은 캡처하지 않습니다.

| 번호 | 통과 조건 | 제출 증거 |
| --- | --- | --- |
| CP1 | 실제 예측 API 동작 | Swagger `/predict` 200 응답 |
| CP2 | API 자동 테스트 세 개 통과 | `3 passed` 터미널 |
| CP3 | Docker 컨테이너에서 API 동작 | 이미지 빌드 결과 + `smoke.py` PASS |
| CP4 | push가 자동 테스트·빌드 실행 | 커밋과 `test`·`build` 성공이 보이는 Actions 화면·실행 링크 |
| CP5 | Docker Hub 자동 업로드·이미지 실행 | `publish` 성공 + Docker Hub Tags + pull한 이미지의 API 확인·이미지 링크 |

### 우리 조 결과 기록

- 조 번호 / 참여자:
- 제출 커밋:
- Actions 성공 실행 링크:
- Docker Hub 이미지 링크: `https://hub.docker.com/r/실제_Docker_ID/bitamin-mlops-week5`
- 이미지 태그 / digest:
- CP1 캡처:
- CP2 캡처:
- CP3 캡처:
- CP4 캡처:
- CP5 캡처:
- 문제와 해결:

실제 캡처를 추가할 때 `![CP1](captures/cp1.png)` 형식으로 연결합니다. 다른 조나 발표조의 캡처를 자기 조 결과로 제출하지 않습니다.

## 막혔을 때 단계별 복구

자기 조 저장소의 **작업 브랜치에서** 실행합니다. 아래 복구는 지정 파일의 현재 변경을 덮어쓰므로 먼저 커밋하거나 백업하세요.

```bash
git fetch week5-snapshot --tags
git restore --source week5-step1 -- week5/test_main.py
git restore --source week5-step2 -- week5/Dockerfile
git restore --source week5-step3 -- .github/workflows/ci.yml
```

publish까지 포함된 워크플로가 필요하면:

```bash
git restore --source week5-final -- .github/workflows/ci.yml
git diff
```

Secrets·Variable은 코드 복구로 생성되지 않습니다. 복구 후 직접 등록하고 커밋·push합니다. 이전 단계와 차이를 보고 싶으면 `git diff week5-step2 week5-step3 -- .github/workflows/ci.yml`을 사용하세요.

## 오류 해결

| 증상 | 확인·해결 |
| --- | --- |
| `No module named week4` | 저장소 루트에서 `python -m pytest week5/test_main.py` 실행 |
| `No module named httpx2`·TestClient 오류 | Python 3.13 가상환경에 `week5/requirements-dev.txt` 재설치 |
| 모델 파일 없음 | `week4/churn_model.joblib` 존재·커밋 포함 여부 확인. 기존 ignore 규칙이 있으면 `git add -f` |
| 모델 버전 경고·로드 오류 | 공통 모델과 공통 requirements를 함께 사용. 기존 환경에 섞지 말고 새 가상환경 사용 |
| Docker daemon 연결 실패 | Docker Desktop 시작 완료·Windows Linux containers·WSL 2 엔진 확인 |
| Docker COPY 실패 | 루트에서 `docker build -f week5/Dockerfile ... .` 실행. 마지막 `.` 필수 |
| `port is already allocated` | 로컬 Uvicorn 종료 또는 기존 실습 컨테이너를 이름 확인 후 종료 |
| 컨테이너 이름 충돌 | `docker ps -a`로 확인 후 해당 실습 컨테이너만 `docker rm -f week5-api` |
| Actions가 실행되지 않음 | 루트 `.github/workflows/ci.yml`, 유효한 YAML, Actions 활성화·사용 한도 확인 |
| publish skipped | 기본 브랜치 실행인지, Variable `ENABLE_DOCKERHUB_PUSH`가 정확히 `true`인지 확인 |
| `unauthorized`·`denied` | Docker ID·Read & Write 토큰·만료일·이미지 저장소 소유 계정 확인 |
| YAML 오류 | `publish:`를 `jobs:` 안에서 `build:`와 같은 깊이에 둠. 필요하면 final 파일 복구 |
| `no matching manifest` | Hub 태그의 두 CPU 아키텍처 확인. STEP 4 멀티 플랫폼 빌드 완료 확인 |
| 빌드가 오래 걸림 | 첫 빌드 패키지 다운로드·두 CPU 이미지 생성 시간 대기. 로그가 진행 중인지 확인 |

추가 확인: [GitHub 워크플로 위치](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows), [Docker 멀티 플랫폼 이미지](https://docs.docker.com/build/ci/github-actions/multi-platform/).
