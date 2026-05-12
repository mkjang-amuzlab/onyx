# 작업 메모리 로그

- 형식: `[YYYY-MM-DD HH:mm KST] 완료: ...`
- [2026-04-07 11:20 KST][소급기록] 완료: Onyx 운영 인수인계 문서 6종(overview/slack/github/sharepoint/web-search/next-steps) 작성.
- [2026-04-07 11:28 KST][소급기록] 완료: 통합 인수인계 문서 99-handover.md 작성.
- [2026-04-07 11:45 KST][소급기록] 완료: SearXNG 컨테이너 배포(8088), onyx_default 네트워크 연결 및 정상 응답 확인.
- [2026-04-07 11:52 KST][소급기록] 완료: Onyx Web Search Provider(SearXNG-Free) 등록/활성화 및 런타임 검색 테스트 성공.
- [2026-04-07 12:00 KST][소급기록] 완료: 기본 Assistant(persona id=0) 정책을 내부검색 우선+웹보조 시스템 프롬프트로 반영.
- [2026-04-07 12:05 KST][소급기록] 완료: 시스템 프롬프트 관리용 PowerShell 스크립트(get/set) 및 기본 프롬프트 파일 생성/검증.
- [2026-04-07 12:11 KST] 완료: 서버 직접 실행용 시스템 프롬프트 관리 스크립트(sh) 생성/배포/검증 완료 (/home/mkjang/workspace/onyx-admin-scripts).
- [2026-04-07 12:12 KST] 완료: Index Settings의 Multipass Indexing / Contextual RAG 역할 코드 기준 분석 및 운영 설명 제공.
- [2026-04-07 12:33 KST] 완료: 운영 검증 1단계 수행(10문항 시나리오 문서 작성 + 서버 precheck 스크립트 배포/실행).
- [2026-04-07 13:15 KST] 완료: 운영 검증 1번 문항을 DB 기준으로 직접 수행해 Slack 인덱싱 현황(채널별 문서 수 포함) 산출.
- [2026-04-07 13:16 KST] 완료: 운영 검증 1번 사용자 답변 판정 수행(채널 수/건수 불일치 확인, 개선안 제시).
- [2026-04-07 13:18 KST] 완료: 운영 검증 1번 재답변 판정 수행(집계 누락 지속 확인, 정답 기준 제시).
- [2026-04-07 13:20 KST] 완료: 시스템 프롬프트 v2 적용(집계형 질문 시 전체 합계 강제 규칙 추가).
- [2026-04-07 13:25 KST] 완료: 운영 검증 1번 재테스트 판정(실제 최신 Slack 집계 818건/22채널 확인, 응답값 34건 불일치로 FAIL).
- [2026-04-07 13:27 KST] 완료: Slack 인덱스 집계 전용 리포트 스크립트(slack-index-report.sh) 생성/서버배포/실행검증 완료.
- [2026-04-07 13:28 KST] 완료: 내부 문서 검색 Top-K 설정 위치 코드 확인(NUM_RETURNED_HITS, MAX_CHUNKS_FED_TO_CHAT, query_request.limit) 및 운영 가이드 제공.
- [2026-04-07 14:16 KST] 완료: 이미지 생성 로컬 모델 지원 여부 코드 확인(기본 provider=openai/azure/vertex_ai, 로컬은 OpenAI 호환 엔드포인트/커스텀 provider 필요).
- [2026-04-07 14:18 KST] 완료: Voice(STT/TTS) 로컬 연동 가능성 코드 확인(openai/azure/elevenlabs provider, openai는 api_base 커스텀으로 호환 엔드포인트 연결 가능) 및 가이드 제공.
- [2026-04-07 14:28 KST] 완료: Agents 3종 생성(사내정책봇/리서치봇/데이터분석봇) 및 도구 매핑 적용(SearchTool 중심, 리서치봇 Web/OpenURL, 분석봇 FileReader/Python).
- [2026-04-07 14:30 KST] 완료: Agents 한글 깨짐 복구(DB ?값 -> UTF-8 한글명/설명 재저장, 데이터분석봇/리서치봇/사내정책봇 정상화).
- [2026-04-07 16:10 KST] 완료: Gemma4 계열 HF 모델(vLLM 적합성) 조사 및 일반/빠른 모델 후보 확정(cyankiwi 26B AWQ, ciocan E4B W4A16 GPTQ, vLLM Gemma4 지원 근거 수집).
- [2026-04-07 17:30 KST] 완료: Onyx 운영 이관(2번) 수행: 구서버(192.168.0.246)에서 DB/env/볼륨(vespa/opensearch/minio) 백업 생성 후 신서버(192.168.0.153)로 전송, `/home/amuzlab-dev/workspace/onyx` 신규 배포 및 DB 복원 완료, 전체 컨테이너 healthy 확인, 웹 헬스(`/api/health`) 정상, 커넥터 4종(Slack/GitHub/SharePoint/Ingestion API) 데이터 유지 확인.
- [2026-04-07 17:33 KST] 완료: SearXNG 신규서버 복원 및 보정(컨테이너 기동, `SEARXNG_BASE_URL`을 `192.168.0.153:8088`로 변경, `onyx_default` 네트워크 연결, Onyx API 컨테이너 내부에서 `http://searxng:8080/search?...&format=json` 200 응답 확인).
- [2026-04-07 17:40 KST] 완료: 246/153 양 서버 Onyx DB에 vLLM 모델 추가(`Gemma4-E4B (Fast)`/`ciocan/gemma-4-E4B-it-W4A16`), 신규 provider `OnPrem-vLLM-246` 생성(`api_base=http://192.168.0.246:8000/v1`), `model_configuration` 및 `llm_model_flow(CHAT)` 반영/검증 완료.
- [2026-04-07 17:43 KST] 완료: 246/153 양 서버 provider 명칭 변경(`OnPrem-vLLM-246` -> `Qwen3-Coder-Next (Coding)`), 연결 모델(`Gemma4-E4B (Fast)`) 참조 무결성 검증 완료.
- [2026-04-07 17:53 KST] 완료: 모델/프로바이더 매핑 재정렬(246/153 공통): provider id1=`Qwen3-Coder-Next (Coding)`(153:8000, Qwen), provider id2=`Gemma4-E4B (Fast)`(246:8000, Gemma), 모델 display_name 보정, CHAT 기본 모델을 Qwen(id1)으로 재설정, api/web 재시작 및 헬스(246/153) 확인.
- [2026-04-07 17:48 KST] 완료: 246/153 양 서버 `Qwen3-Coder-Next (Coding)` 및 `Gemma4-E4B (Fast)` provider에 더미 API 키(`sk-onprem-dummy-key`) 저장(ORM 경로), 마스킹 조회 검증(`sk-o...-key`), api_server 재시작 반영.
- [2026-04-07 17:58 KST] 완료: 사내 운영용 에이전트 5종 생성/배포(246/153 공통) - `Security Guard`, `Policy Compliance`, `Workflow Automation`, `Knowledge Curator`, `Ops Monitor`; 시스템/태스크 프롬프트, 모델 기본값(Qwen/Gemma), 툴 매핑 반영 및 검증 완료. 운영 설계 문서 `07-agents-blueprint.md` 추가.
- [2026-04-07 18:09 KST] 완료: 에이전트 5종 한글명/한글 설명으로 복구(UTF-8 재저장), Deep Research 오류 원인 확인(`OPENAI_API_KEY` 미설정), 246/153 `.env`에 `OPENAI_API_KEY=sk-onprem-dummy-key` 추가 후 `api_server` 강제 재생성 반영.
- [2026-04-07 18:13 KST] 완료: Deep Research 전용 `딥리서치봇` 생성(기본 모델 `Gemma4-E4B (Fast)`, 툴 `internal_search/open_url/web_search/research_agent`) 및 UTF-8 손상 복구. 246/153 `api_server` 헬스 재확인(모두 healthy).
- [2026-04-07 18:20 KST] 완료: 사용자 요청에 따라 246 우선 에이전트 런타임 테스트 수행(6종 응답/모델 매핑 확인), 이후 153 동기화 반영. 153 반영 중 인코딩 경로로 이름 손상(`?`) 발생해 UTF-8 안전 경로로 즉시 복구. 최종 상태: 246/153 모두 한글 에이전트명 정상 + 모델 오버라이드 일치 + 딥리서치봇(Gemma 131072) 준비 완료.
- [2026-04-07 18:30 KST] 완료: 에이전트 운영 템플릿 반영(246 우선 적용 후 153 동기화) - `starter_messages`를 각 에이전트(보안가드봇/정책준수봇/업무자동화봇/지식큐레이터봇/운영관제봇/딥리서치봇)별 5개씩 총 30개 등록, DB 검증(`jsonb_array_length=5`) 완료.
- [2026-04-07 18:42 KST] 완료: 에이전트 운영 검증 산출물 정리 - 서버 실행형 검증 스크립트 `scripts/agent-validation-report.sh` 추가 및 오늘자 리포트 `08-agent-validation-2026-04-07.md` 작성.
- [2026-04-07 18:55 KST] 완료: Windows 자동 SSH 도구 구성 - `PuTTY/plink` 설치, 서버별 host key fingerprint 고정 비대화형 접속 검증(246/153), 재사용용 스크립트 `scripts/ssh-auto.ps1` 추가.
- [2026-04-07 19:05 KST] 완료: SSH 키 기반 접속 전환 - 로컬 `~/.ssh/id_rsa.pub`를 246/153 `authorized_keys`에 등록, 비밀번호 없는 접속(`ssh -i id_rsa -o BatchMode=yes`) 검증 완료. `ssh-auto.ps1`을 key/password 선택 지원으로 업데이트(기본 key).
- [2026-04-07 19:18 KST] 완료: 기존 작업 재개 - 246/153 양 서버 에이전트 실측 재검증(IDs 4-9 이름/모델/starter=5/툴 매핑 동일) 완료. 서버 실행형 `agent-validation-report.sh`를 환경 맞춤(`relational_db`, DB `postgres`)으로 보정/재배포하고 양 서버에서 리포트 생성 PASS 확인.
- [2026-04-07 19:45 KST] 완료: 에이전트 E2E 채팅 테스트 수행(246 우선, 153 동기화 검증). 246 첫 실행 5/6 후 persona 7 타임아웃(504) 재시도로 통과, 153은 6/6 즉시 통과. persona 9의 `research_agent(tool_id=8)` 매핑이 런타임 `KeyError: ResearchAgent`를 유발해 양 서버에서 해당 매핑 삭제 후 정상화.
- [2026-04-07 20:02 KST] 완료: 504 재발 방지 튜닝 - no-letsencrypt nginx 템플릿의 누락된 proxy timeout(connect/send/read) 지시어를 양 서버에 보정하고 nginx 재시작 반영. 246/153 모두 `app.conf` 기준 `300s` 타임아웃 확인 및 `/api/health` 정상.
- [2026-04-08 10:55 KST] 완료: API 레벨 timeout 튜닝 - 코드 기준 `LLM_SOCKET_READ_TIMEOUT` 기본값(60s) 확인 후 양 서버 `.env`에 `LLM_SOCKET_READ_TIMEOUT=180`, `REQUEST_TIMEOUT_SECONDS=120` 반영 및 `api_server` 재기동. 실측 검증: 246에서 136초 장문 응답 `200`/정상 완료, 153도 E2E 응답 정상.
- [2026-04-08 11:15 KST] 완료: Discord 연동 준비 착수 - Onyx 코드/엔드포인트 기준 Discord bot+connector 지원 확인, 운영 런북 `12-discord-integration-runbook-2026-04-08.md` 작성, 관리자 API 기반 자동 초기화 스크립트 `scripts/setup-discord-bot.sh` 추가.
## 2026-04-08 (PPT 시각자료 보강)
- 요청: 직원 대상 Onyx 소개 PPT에 구조도/이미지를 추가해 이해도 개선.
- 반영 기준: Onyx Admin Docs Overview 항목(Admin Panel, Core Admin Features) 기반.
- 작업 내용:
  - 기존 PPT 3종에 시각 슬라이드 2장씩 추가.
  - 추가 슬라이드 1: "Onyx 운영 구조도 (Overview 기반)"
    - 사용자/Onyx UI/Admin Panel/API/LLM(vLLM)/검색인덱스/커넥터(Slack/SharePoint/GitHub) 흐름도.
  - 추가 슬라이드 2: "Admin Overview 핵심 항목"
    - Admin Panel 중심으로 Language Models, Connectors, Actions & MCP, Agents, Slack Bot, User Management, Workspace Analytics, Advanced Configs, Plans & Billing 맵.
- 수정 파일:
  - docs/onyx-deployment/presentations/onyx-employee-overview-10slides.pptx (13장)
  - docs/onyx-deployment/presentations/onyx-employee-detailed-15slides.pptx (18장)
  - docs/onyx-deployment/presentations/onyx-employee-training-25slides.pptx (28장)
## 2026-04-08 (PPT md 원본화 + 재생성 체계)
- 요청: PPT 내용을 md로 정리하고, md 기반으로 다시 수정/재생성 가능하게 준비.
- 조치:
  - `presentations/sources` 폴더 생성.
  - 공통 Overview 정리 문서 작성:
    - `presentations/sources/00-onyx-admin-overview-core.md`
  - 덱 원본 md 작성:
    - `presentations/sources/deck-overview-10.md`
    - `presentations/sources/deck-detailed-15.md`
    - `presentations/sources/deck-training-25.md`
  - 생성 스크립트 작성:
    - `scripts/build_presentations_from_md.py`
    - 지원 타입: `title`, `section`, `bullets`, `diagram_architecture`, `diagram_admin_features`
  - 실행 스크립트 작성:
    - `scripts/build-presentations-from-md.sh`
    - `scripts/build-presentations-from-md.ps1`
- 한글 깨짐(??? 대응:
  - python-pptx 텍스트 런에 동아시아 폰트(`a:ea`)를 강제 지정하도록 수정.
- 결과:
  - md 기반 재빌드 성공
  - `onyx-employee-overview-10slides.pptx` (13장)
  - `onyx-employee-detailed-15slides.pptx` (18장)
  - `onyx-employee-training-25slides.pptx` (28장)
## 2026-04-08 (onyx.app 기준 재정리)
- 요청: onyx.app 내용을 참고해 발표 자료를 다시 정리.
- 조치:
  - `presentations/sources/00-onyx-app-website-summary.md` 신규 작성.
  - 핵심 메시지 반영: Docs/Apps/People 연결, Reliable Responses, Customizable, Feature Rich, Permission-Aware.
  - 덱 원본 업데이트:
    - `deck-overview-10.md`
    - `deck-detailed-15.md`
    - `deck-training-25.md`
  - md 기반 PPT 재빌드 완료.
- 결과:
  - `onyx-employee-overview-10slides.pptx` (13장)
  - `onyx-employee-detailed-15slides.pptx` (18장)
  - `onyx-employee-training-25slides.pptx` (28장)
## 2026-04-08 (기술 관점 md 초안 작성)
- 요청: onyx 소개 자료를 더 기술적인 측면으로 md 형태로 작성.
- 신규 문서 작성:
  - `presentations/sources/01-onyx-technical-overview.md`
- 포함 내용:
  - 목표/비목표, 기준 아키텍처, 컴포넌트 책임, 질의/인덱싱 데이터 흐름
  - 모델 라우팅 전략, 커넥터 운영(Slack/GitHub/SharePoint)
  - 보안/감사, 관측성 지표, 성능/용량, 장애 대응, 배포 프로세스, 우선 과제
## 2026-04-08 (질의 런타임 + 기술 FAQ 문서화)
- 요청: Onyx 질의 처리 동작을 md로 저장하고 다이어그램 포함, 아래 3개 질문 답변 정리.
- 신규 문서 작성:
  - `docs/onyx-deployment/13-onyx-query-runtime-and-faq.md`
- 포함 내용:
  - E2E 질의 처리 시퀀스(mermaid)
  - 컴포넌트 아키텍처(mermaid)
  - ACL 필터 동작 흐름(mermaid)
  - FAQ 답변:
    1) Deep Research의 로컬 LLM 동작 조건(50k+ context, tool-calling)
    2) Vespa vs OpenSearch 비교 및 운영 권장
    3) ACL 생성/주입/결합 규칙(OR within ACL + AND with other filters)
## 2026-04-08 (ACL 상세 + DGX SPARK 모델 리서치)
- 요청: ACL 동작 상세 설명 + DGX SPARK(GB10 128GB)에서 tool-calling/50k+ context 가능한 최신 고성능 모델 조사.
- 신규 문서 작성:
  - `docs/onyx-deployment/14-acl-deep-dive-and-dgx-spark-model-research.md`
- 핵심 반영:
  - ACL 생성/주입/결합 규칙(OR/AND) 및 디버깅 체크리스트
  - DGX Spark 공식 스펙(128GB unified, up to 200B inference)
  - 모델 후보: Mistral Small 4, Qwen3.5-122B-A10B, Qwen3-Coder-Next
  - vLLM tool-calling 안정성 주의사항(auto vs required)
## 2026-04-14 (SMB 접속 원인 분석 + Qwen3.5 Tool Calling 재검증)
- 요청: 153 SMB 접속 불가 원인 파악, Qwen3.5 툴 호출 재테스트, 진행 현황 기록.
- 점검/조치:
  - `로컬 -> 192.168.0.153 SMB` 장애 원인 확인: `smbd/nmbd` 비활성(inactive)으로 445 미리스닝.
  - 153에서 Samba 서비스 기동/영구화 완료: `systemctl enable --now smbd nmbd`.
  - 검증 완료: `\\192.168.0.153\\spark_home` 윈도우에서 드라이브 마운트/조회 성공.
  - 153 vLLM 런타임 재확인: `tool_call_parser=qwen3_coder`, `reasoning_parser=qwen3` 반영.
  - 사용자 반영사항(`qwen3.5-122b-int4-autoround.yaml` 기반 템플릿 변경) 적용 후 재검증.
- 테스트 결과(vLLM 직접 API):
  - `chat/completions` 강제 tool call: 5/5 성공.
  - `responses` 강제 tool call: 5/5 성공.
  - `responses` auto tool call: 5/5 성공.
  - 추가 반복(`responses` 강제) 3/3 성공.
  - 직후 로그 확인: `500 Internal Server Error` / `AssertionError(assert content is not None)` 재발 없음.
- 테스트 결과(Onyx API E2E):
  - `/api/search/send-search-message` 정상(검색 문서 반환 확인).
  - `/api/chat/send-chat-message` 일반 대화 정상 응답.
  - 단, 일부 검색 결합 채팅에서 간헐 빈 응답 재현(로그: `LLM packet is empty`).
- 결론:
  - 템플릿 변경 후 vLLM 툴콜 경로는 정상화됨.
  - 잔여 이슈는 Onyx 채팅 경로의 간헐 빈 패킷 처리(모델/스트리밍 조합)로 분리 대응 필요.
## 2026-04-14 (모델 선택 미반영 이슈 진단)
- 요청: Onyx 채팅창에서 모델 선택 시 변경이 안 되는 현상 원인 확인.
- 진단 결과:
  - `PUT /chat/update-chat-session-model` 호출은 정상 `200` 응답.
  - DB `chat_session.current_alternate_model` 값이 세션별로 실제 변경됨(예: Gemma4-E4B / Qwen3.5 값 교차 저장 확인).
  - 즉, "모델 전환 자체"는 실패가 아니라 저장/반영됨.
  - 다만 동일 시점에 `LLM packet is empty` 경고 및 일부 `model encountered an error during generation`가 발생해 체감상 변경이 안 된 것처럼 보임.
  - 추가 관찰: `Model '<model_id>' not found in LiteLLM. Falling back to 32000 tokens.` 경고가 지속 출력(토큰 메타 fallback 경고, 모델 호출 자체와는 별개).
- 결론:
  - UI 모델 변경은 정상 동작.
  - 현재 체감 문제의 본질은 모델 전환 실패가 아니라, Qwen/Gemma 경로의 간헐 생성 불안정(빈 패킷/생성 에러).
## 2026-04-14 (Qwen 전환 후 채팅 에러 원인 분석/안정화)
- 요청: Qwen으로 변경 후 Onyx 채팅에서 결과 미출력/에러 발생 원인 확인.
- 주요 진단:
  - `onyx-api_server-1`가 `unhealthy` 상태였고, healthcheck timeout(20s) 반복 확인.
  - API 로그에서 동시 발생 확인:
    - `litellm.APIConnectionError: ... Bad file descriptor`
    - `Vespa 504 Gateway Timeout` / `Timeout while waiting for danswer_index.num0`
    - `Function timed out after 600 seconds`
    - `LLM packet is empty (finish_reason=tool_calls, tool_calls=[])`
  - 153 vLLM 직접 점검 결과:
    - `Intel/Qwen3.5-122B-A10B-int4-AutoRound` 모델 API는 정상 응답.
    - tool-calling(비스트리밍/스트리밍) 모두 정상 형식(JSON arguments)으로 반환 확인.
- 조치:
  - 246에서 `onyx-api_server-1` 재시작 수행.
  - 재기동 과정(마이그레이션/인덱스 연결) 확인 후 최종 `healthy` 복귀 확인.
- 현재 판단:
  - 모델 전환 자체 고장보다는, 검색/도구 호출이 섞인 고부하 구간에서 Onyx API + Vespa 타임아웃이 겹치며 실패한 케이스.
  - vLLM(Qwen) 단독 상태는 정상.
- 운영 메모:
  - 동일 증상 재발 시 우선순위: (1) API health (2) Vespa timeout (3) LLM empty packet 순으로 확인.
## 2026-04-14 (정확도 우선 프리셋 적용: gpt-oss-120b)
- 요청: 답변 정확도 개선을 위한 운영 설정 튜닝.
- 적용 대상: 192.168.0.246 Onyx 운영 DB/API.
- 조치 내용:
  1) LLM 기본 제공자 전환
     - `llm_provider.id=6 (gpt-oss-120b)`를 기본 제공자로 설정(`is_default_provider=true`)
     - `default_model_name='gpt-oss-120b'` 설정
  2) 기본 Assistant( persona id=0 ) 정확도 프롬프트 강화
     - 추측 금지, 근거/출처 요구, 충돌 시 내부 문서 우선, 수치/범위 명시, 웹검색 사용 조건 명시
     - 출력 포맷 고정: Answer / Evidence / Confidence / Missing info
     - `default_model_configuration_id=10 (gpt-oss-120b)` 지정
  3) 사용자 기본 모델 지정
     - 실사용자 계정(`admin@onyx-demo.com`, `mkjang@amuzlab.com`, `test@amuzlab.com` 등) 기본 모델을 `gpt-oss-120b`로 지정
     - `anonymous`/`api_key__*` 계정은 제외
  4) 반영 안정화
     - `onyx-api_server-1` 재시작 후 health `healthy` 확인
- 참고 관찰:
  - 기존 정확도 저하 원인 중 하나로 Qwen 경로의 `LLM packet is empty (finish_reason=tool_calls)` 로그가 반복 관찰됨.
  - 이번 변경은 모델 기본값 + 응답 규칙 강화를 통해 환각/추측 답변을 줄이는 방향.
- [2026-04-15 21:47 KST] 완료: 246 서버에 LiteLLM 프록시 구축(/home/mkjang/litellm), 포트 4001 사용, chat-primary(153)·chat-fast(246) 라우팅 검증 완료.
- [2026-04-15 21:59 KST] 완료: LiteLLM 공급망 이슈 대응. 246 litellm-proxy 버전(1.82.3) 및 litellm_init.pth 부재 확인, 이미지 digest(sha256:9e1536c6...)로 docker-compose 고정 후 재기동.
- [2026-04-15 22:04 KST] 완료: LiteLLM 1차 최적화 적용(246). fallback(chat-primary->chat-fast), timeout/retry 유지, Onyx Postgres 연동(litellm DB) 후 virtual key 발급 및 key별 rpm/tpm 제한 검증 완료.
## 2026-04-16 153 동기화 작업
- 요청: 246 기준 Onyx 운영 구성을 153 서버에 동기화
- 수행:
  - 246 `/home/mkjang/onyx/deployment/docker_compose/{docker-compose.yml,.env}`를 153 `/home/amuzlab-dev/workspace/onyx/deployment/docker_compose/`로 복사
  - 153 `.env`에서 `WEB_DOMAIN`만 `http://192.168.0.153`으로 유지
  - `docker compose pull web_server api_server background inference_model_server indexing_model_server`
  - `docker compose up -d` 재기동
- 결과:
  - 153 Onyx 컨테이너 이미지가 `craft-latest`로 정렬됨
  - `ENABLE_CRAFT=true` 반영
  - `http://localhost` 200 확인, `onyx-api_server-1` health 정상
## 2026-04-16 153 LLM 모델 동기화
- 요청: 246 기준 LLM 모델/플로우를 153에 동기화
- 사전 상태:
  - 153 기존 Provider: Qwen3.5-122B-A10B, Gemma4-E4B (Fast)
  - 153 기존 CHAT flow: 2개
- 작업 방식:
  - 참조 제약(persona/image_generation_config) 때문에 삭제-재삽입 대신 upsert 방식 적용
  - 246 기준 Provider/Model 반영:
    - Provider: Local LLM(openai_compatible), gemma4-e4b-it(openai_compatible), LiteLLM(litellm_proxy)
    - Model: chat-primary(Local LLM), ciocan/gemma-4-E4B-it-W4A16(gemma4-e4b-it), chat-fast/chat-primary(LiteLLM)
  - CHAT flow 재구성(기본값 포함 4개):
    - default: Local LLM/chat-primary
    - non-default: gemma4-e4b-it/ciocan..., LiteLLM/chat-fast, LiteLLM/chat-primary
  - 반영 후 `api_server/background/web_server` 재시작
- 검증:
  - `onyx-api_server-1` healthy
  - `http://localhost` 200
## 2026-04-16 153 Onyx 중지
- 요청: 153 서버 Onyx 임시 중지 (246 안정화 후 재작업 예정)
- 수행: `/home/amuzlab-dev/workspace/onyx/deployment/docker_compose`에서 `docker compose down`
- 결과: onyx 컨테이너 전체 중지/삭제 완료, 서비스 중단 상태 확인
- 참고: `onyx_default` 네트워크는 다른 컨테이너 사용으로 미제거(`Resource is still in use`)되었으나 서비스 중지에는 영향 없음
## 2026-04-16 Slack 응답 무응답 점검 (246)
- 점검 대상: 246 Onyx Slack Integration 런타임
- 확인 결과:
  - Slack listener 프로세스 정상 실행: `python onyx/onyxbot/slack/listener.py`
  - Slack 이벤트 수신 정상(로그에 `process_message start`, `Received Slack message` 다수 확인)
  - 무응답 주요 원인 로그 확인:
    - `Skipping message since it does not contain a question mark`
    - `Skipping message: OnyxBot only responds to tags in this channel`
- 조치:
  - `slack_channel_config` 기본 설정 완화
    - `respond_tag_only: false`
    - `answer_filters: ["well_answered_postfilter"]` (questionmark_prefilter 제거)
- 추가 이슈:
  - Slack API scope 부족 경고 확인: `missing_scope`, `needed: reactions:write`
  - 이는 반응(이모지 추가/제거) 실패 원인이며 답변 자체를 항상 막는 치명 오류는 아님
- [2026-04-16 14:39 +09:00] 완료: 246 LiteLLM 모델 alias 변경(chat-primary->Gemma4-26B-A4B, chat-fast->Gemma4-E4B) 및 Onyx DB model_configuration(id14/id15) 이름·표시명 동기화, onyx-api_server 재시작 반영.
- [2026-04-16 15:10 +09:00] 완료: 246 Onyx 관리자 계정 이메일 변경(mkjang@amuzlab.com -> onyx_admin@amuzlab.com), ADMIN 권한/활성 상태 유지 확인.
- [2026-04-16 15:13 +09:00] 정정 완료: 관리자 이메일 변경 대상 수정(admin@onyx-demo.com -> onyx_admin@amuzlab.com). 이전 오변경분(mkjang 계정)을 mkjang@amuzlab.com으로 원복 후 적용.
- [2026-04-16 15:29 +09:00] 완료: 246 일반 사용자 기본 앱 모드 변경(BASIC/SLACK_USER => SEARCH). Agents 깨짐(???) 점검 결과 persona name/description/system/task에 손상 문자 미검출(데이터 정상).
- [2026-04-16 15:37 +09:00] 완료: 246 Slack bot 기본 channel config에 persona_id=3(사내정책봇, internal_search 전용) 적용 및 onyx-background 재시작. Slack 응답 경로를 내부검색 우선(실질 강제)으로 전환.
- [2026-04-16 15:39 +09:00] 완료: 246 Slack bot 기본 persona를 사내정책봇(id=3)에서 리서치봇(id=2)으로 변경(내부검색 우선 + 필요 시 웹 보강), onyx-background 재시작 반영.
- [2026-04-16 15:40 +09:00] 완료: 246 Agents starter_messages(예시 질문) 깨짐 복구. persona id 4~9의 starter_messages를 정상 한글 JSON으로 재저장.
- [2026-04-16 15:44 +09:00] 점검: 슬랙 사내검색 우선 동작 재확인. 리서치봇(id=2) system/task prompt를 '항상 internal_search 먼저' 정책으로 강화. 로그에서 Slack message 처리(success=True) 및 일부 쿼리(명시적 사내문서 요청)에서 linked_docs=19/internal_search 호출 확인.
- [2026-04-16 15:50 +09:00] 완료: Slack 질문 정책 반영(리서치봇 id=2). 내부검색 1차+재검색 2차 강제 후 근거 부족 시 '내부 미확인 참고답변' 형식으로 응답하도록 system/task prompt 강화 및 background 재시작.

- 2026-04-16 16:10 KST: Slack bot no-response incident on 246 fixed. Root cause was tenant lock (public:da_lock:slack_bot) after background restart; lock TTL + acquisition interval delayed reconnection. Verified recovery with log: Started SocketModeClient at 07:09:41.

- 2026-04-16 16:25 KST: Slack retrieval check for channel C08801Z2PPF. Logs show bot receives events, but non-mention message was skipped due @OnyxBot-only setting. Mentioned query triggered retrieval, yet many 'No hits found' for C088* document IDs around 07:22 KST, indicating partial/missing indexed chunks for recent channel messages.

- 2026-04-16 16:33 KST: Investigated missing Slack answer for '디지털미디어이노베이션기술개발 과제 평가 장소'. Slack source message exists in #어뮤즈랩-팀장 (C08801Z2PPF, ts 1773890400.334629) via Slack search, but Onyx retrieval logs show repeated 'No hits found' for related C088* doc chunks during Slack bot query. Indicates indexing/chunk retrieval gap (not source absence).

- 2026-04-16 16:45 KST: Re-indexed Slack connector for target channel #어뮤즈랩-팀장 only via temporary connector filter (connector id=7 -> channels=[어뮤즈랩-팀장], cc_pair id=2 REINDEX). First run attempt 893 failed due mojibake channel string; retried with unicode-escaped channel name and attempt 894 completed SUCCESS (57/57 batches, finished at 07:44:22 UTC). Restored connector config back to {} after kickoff.

- 2026-04-16 16:49 KST: Post re-index verification complete. Document C08801Z2PPF__1773890400.334629 is now searchable in Vespa with 3 chunks, and chunk 1 content includes exact line: '평가장소 : 서울 상연재 서울역점 R6(중구 한강대로 416, 서울스퀘어 4층)'.

- 2026-04-16 17:02 KST: Re-indexed Slack channel #ax only (connector 7 with temporary channels=[ax], cc_pair=2 REINDEX). Index attempt 896 SUCCESS (2/2 batches). Restored connector config to {}. DB verification shows 27 docs indexed for C0ARMS1B5BP__* with last_synced around 07:58 UTC.
- 2026-04-16 17:03 KST: Updated Slack default persona(id=2, 리서치봇) task_prompt to enforce channel-line in responses: 'Channel: #<channel_name>' or fallback 'Channel ID: <channel_id>' at beginning of every answer.

- 2026-04-16 17:20 KST: Updated Slack default persona(id=2) prompt to support explicit web/general/external-search requests. New override: when user explicitly requests web search, do not abstain due to missing internal evidence; answer using external sources with URLs/dates. Noted default Slack channel config still has respond_tag_only=true (mention required).

- 2026-04-16 18:00 KST: Team-lead channel removal reindex completed. Slack cc_pair=2 reindex attempt 898 SUCCESS (513/513, docs_indexed=7940, new_docs=363). Connector config kept as regex-exclude for #어뮤즈랩-팀장: channels=[^(?!어뮤즈랩-팀장$).*$], channel_regex_enabled=true.
- 2026-04-16 18:01 KST: Post-check: relational DB still retains metadata rows (document table) for C08801Z2PPF, but Vespa query by C08801Z2PPF__* returned 0 hits after reindex (non-searchable).
- [2026-04-16 18:25 +09:00] 완료: 현재까지 운영 내용 문서화. `15-운영-현황-스냅샷-2026-04-16.md`(상태 요약) 및 `16-팀-공유-런북.md`(설치~운영 공유용) 신규 작성. Slack/SharePoint/GitHub/모델 라우팅/장애 체크리스트 포함.
- [2026-04-16 18:29 +09:00] 완료: 팀 공유용 1페이지 체크리스트 문서 `17-배포-운영-체크리스트-1page.md` 신규 추가(배포 전 점검, 모델/커넥터 검증, 장애 트리아지, Go/No-Go 기준 포함).
- [2026-04-16 18:37 +09:00] 완료: 체크리스트 문서 2종 분리 작성(`18-배포-운영-체크리스트-상세.md`, `19-배포-운영-체크리스트-초간단.md`) 및 전사 공유용 안내문(`20-사내-공유용-Onyx-안내.md`) 추가. 설치 목적/현재 구성/사용법/운영 원칙/문의 방식 포함.
- [2026-04-16 18:46 +09:00] 완료: Onyx 코드레벨 질의 처리 분석 문서 신규 작성(`21-onyx-내부-질의처리-코드레벨-분석.md`). API 진입->LLM loop->tool runner->SearchTool->retrieval->save_chat_turn 전체 체인과 Mermaid 흐름도/시퀀스 다이어그램 포함.
- [2026-04-16 18:52 +09:00] 완료: `21-onyx-내부-질의처리-코드레벨-분석.md`에 LLM 사용 구조 섹션 추가(메인 생성, 툴 의사결정, 검색 보조추론, Deep Research/멀티모델 분기). 모델 교체 시 검증 포인트(답변 품질 + tool calling 품질) 명시.
- [2026-04-16 19:00 +09:00] 완료: 일일 작업 요약 문서 `2026-04-16-작업일지.md` 생성(운영 이슈 처리, 설정 변경, 문서화 산출물, 다음 작업 포함).
- [2026-04-17 09:06 +09:00] 완료: 발표용 통합 문서 `22-onyx-통합-발표용-설치-세팅-이슈-가이드.md` 신규 작성. 설치/세팅/이슈/사용가이드와 vLLM 서빙 방법(직접 실행, 레시피 실행, Onyx 등록, 운영 트러블슈팅) 포함.
- [2026-04-17 09:12 +09:00] 수정: 발표용 통합 문서 Slide 09 업데이트. `spark-vllm-docker` 기반 이미지 생성 경로 추가 및 Gemma4 Docker 실행 커맨드를 운영 커맨드로 교체.
- [2026-04-17 09:15 +09:00] 수정: 발표용 통합 문서 Slide 09에 vLLM 운영 커맨드 추가(docker logs -f, docker stop, docker run 재기동 예시).
- [2026-04-17 09:20 +09:00] 수정: `23-onyx-설치-상세-가이드.md`의 모델 연결/커넥터 연결 섹션을 Onyx 공식 문서 링크 기반으로 개편(AI Models Overview, Custom Inference Provider, LiteLLM Proxy, Slack/GitHub/File/SharePoint 공식 가이드 링크 반영).
- [2026-04-17 09:24 +09:00] 수정: `23-onyx-설치-상세-가이드.md`에 Slack Integration(OnyxBot) 섹션 추가. 공식 링크(`slack_bot_setup`, Slack Bot overview)와 요약 절차/운영 권장사항 반영.
- [2026-04-17 09:28 +09:00] 수정: `23-onyx-설치-상세-가이드.md`에 NAS 문서 인덱싱 실사례 추가. SMB 마운트 절차, 운영 경로(`/mnt/nas/amuzlab/SharePoint/Amuzlab_DOC/02. 프로젝트/32.채널영상분석시스템 개발`), fstab 자동 마운트 예시, 검증/재인덱싱 절차 반영.
- [2026-04-17 09:34 +09:00] 완료: `22-onyx-통합-발표용-설치-세팅-이슈-가이드.md`와 `23-onyx-설치-상세-가이드.md`를 통합하여 `24-onyx-통합-설치-운영-가이드.md` 생성(Part A 발표용 + Part B 설치/운영 상세 구조).
- [2026-04-17 09:40 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md`에서 발표용(Part A/Slide) 내용 제거. 설치/운영 실무 가이드 전용 문서로 정리.
- [2026-04-17 09:44 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md` 단일 문서 스타일 정리(중복 제목/중복 기준 문구 제거).
- [2026-04-17 09:47 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md` 상단에 링크형 목차(TOC) 추가.
- [2026-04-17 09:54 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md` 가독성 개선. 어려운 용어 한 줄 설명 추가 및 외부 공식 참고 링크(Docker, Compose, vLLM, LiteLLM, Onyx Connectors, Ubuntu CIFS) 보강.
- [2026-04-17 10:01 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md`에 부록 추가. (A) 사내검색 RAG 처리 절차+Mermaid 흐름도, (B) Deep Research 처리 절차+Mermaid 흐름도 및 운영 팁 반영.
- [2026-04-17 10:07 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md`에 부록 C(하이브리드 RAG) 추가. 키워드+의미 검색 병행 방식, 용어 쉬운 설명(임베딩/BM25/RRF/리랭킹/ACL), Mermaid 흐름도 및 운영 팁 반영.
- [2026-04-17 10:13 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md` 부록 C에 향후 개선 아이디어 추가(LightRAG/RAG-Anything 참고 링크 + 그래프 신호 결합, 멀티모달 확장, 2단계 검색, 파일럿 A/B 테스트 제안).
- [2026-04-17 10:20 +09:00] 수정: `24-onyx-통합-설치-운영-가이드.md` 목차에 부록 A/B/C 링크 항목 추가.
- [2026-04-17 10:28 +09:00] 수정: 권장 개선사항 반영. `24-onyx-통합-설치-운영-가이드.md`에 (1) 경로 템플릿(`/home/<ONYX_USER>/onyx`) 적용, (2) NAS 자격증명 파일 기반 보안 마운트(`credentials=/root/.smbcredentials`)로 변경, (3) 커넥터 공통 링크 정리, (4) 운영 로그 점검 명령 추가, (5) 버전 고정 권장 섹션 추가.

- 2026-04-17: 24번 통합 가이드 문서 제목을 'Onyx 온프레미스 구축·운영 실무 가이드'로 변경하고 목적 문구를 모델/커넥터/인덱싱 검증 중심으로 보강.
- [2026-04-17 19:32 +09:00] 수정: 24-onyx-통합-설치-운영-가이드.md에 17. SearXNG 웹서치 엔진 (소개/설치/운영) 섹션 추가 및 목차 링크 반영(개요/설치 예시/Onyx 연동/운영 체크리스트/트러블슈팅 포함).
- [2026-04-17 19:38 +09:00] 수정: 24번 문서 부록 A/B/C를 쉬운 한국어 중심으로 개편. 흐름도 노드 한글화 및 영어 용어 주석(ACL/internal_search/citation/RRF/Deep Research 등) 추가.
- [2026-04-17 19:45 +09:00] 수정: 부록 A/B/C에 박스+화살표 기반 텍스트 다이어그램(ASCII) 추가. 기존 mermaid 유지 + 쉬운 그림형 요약 병행.
- [2026-04-27 12:05 +09:00] 완료: 전체 NAS 사내문서 인덱싱 자동화 스크립트 추가(docs/onyx-deployment/scripts/index-all-nas-docs.py). /mnt/nas/amuzlab/SharePoint/Amuzlab_DOC 전체 스캔, 지원 확장자 필터링, zip 청크 생성, Onyx File Connector 업로드/생성/추가/인덱싱 트리거 기능 포함. 24번 운영 가이드에 사용법 반영.
- [2026-05-11 00:00 +09:00] 완료: MCP 출력 정책을 `search_indexed_documents` / `search_web` / `open_urls`에 적용. `search_web`는 `masked_snippet`, `open_urls`는 `summary_only`로 후처리하고 `policy` 메타데이터를 반환하도록 정리. 운영 문서 `2026-05-11-mcp-output-policy-runbook.md` 신규 작성.
- [2026-05-11 00:00 +09:00] 진행: 111 MCP 서버 기동 이슈를 좁히는 중. 111 live container에서 `mcp_server/resources/document_sets.py`가 `get_accessible_document_sets()`를 요구하지만, local `utils.py`에는 해당 helper가 없어 import 에러 발생. helper를 추가해 111 재기동 준비 중.
- [2026-05-11 00:00 +09:00] 완료: 111 MCP 서버 재기동 성공. `get_accessible_document_sets()` helper 추가 후 `onyx-mcp_server-1`이 `Up` 상태로 전환되었고 `curl http://127.0.0.1:8090/health`가 `healthy`를 반환함. 246/111 모두 MCP output policy + search_web policy 적용 상태.
- [2026-05-11 00:00 +09:00] 완료: `internal/main`에 MCP output policy + 111 helper 변경사항 커밋 및 푸시 완료. commit `f1efc8d` (`Add MCP output policy and 111 document set helper`)를 `origin/internal/main`에 반영.
- [2026-05-11 00:00 +09:00] 완료: `search_web` 후처리를 강화. snippet/body 계열 필드를 요약한 뒤 마스킹하도록 바꾸고, 운영 문서 `2026-05-11-mcp-output-policy-runbook.md`를 해당 동작에 맞게 갱신함.
- [2026-05-11 00:00 +09:00] 완료: MCP 출력에 인명 비식별화 추가. `MCP_SERVER_REDACT_PERSON_NAMES=true` 기본값으로 MCP 출력 후처리에서만 사람 이름을 마스킹하도록 확장하고, `search_indexed_documents`/`search_web` 결과에 대한 unit test를 추가함.
- [2026-05-12 00:00 +09:00] 완료: Onyx custom git 운영 방식 정리. 수정된 파일 자체를 `onyx_custom` 저장소에 보관하고, 변경 이유/절차는 별도 문서로 남기는 구조로 합의함. upstream 변경은 overwrite가 아니라 merge/rebase로 흡수하는 방향으로 기록함.
- [2026-05-12 00:00 +09:00] 진행: `internal/main` 기준 변경 파일만 다른 체크아웃으로 내보내는 `tools/export_internal_main_overlay.ps1` 초안 추가. dirty worktree와 무관하게 커밋된 overlay만 내보내는 흐름으로 시작함.
