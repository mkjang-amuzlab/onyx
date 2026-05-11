# MCP 출력 정책 운영 문서

## 목적
Onyx MCP 서버의 응답이 원문 그대로 외부로 노출되지 않도록 하고, 민감정보 비식별화와 요약/가공 규칙을 운영 관점에서 일관되게 관리한다.

## 현재 적용 정책
- `search_indexed_documents` -> `masked_snippet`
- `search_web` -> `masked_snippet` with summary applied to snippet/body fields
- `open_urls` -> `summary_only`
- `raw` 모드는 `MCP_SERVER_OUTPUT_POLICY_MODE=raw` 이면서 `MCP_SERVER_ALLOW_RAW_OUTPUT=true`일 때만 허용

## 정책 동작 방식
1. 입력 텍스트는 `redact_sensitive_text()`로 1차 마스킹한다.
2. 출력 텍스트는 `redact_sensitive_output_text()`로 추가 마스킹한다.
3. `search_web`는 결과의 snippet/body 계열 필드를 짧게 줄인 뒤 반환한다.
4. `open_urls`는 `build_safe_summary()`로 본문을 요약한 뒤 반환한다.
5. 모든 MCP 응답에는 `policy` 메타데이터를 붙여 실제 적용 모드를 확인할 수 있게 한다.

## 환경 변수
- `MCP_SERVER_REDACT_SENSITIVE_INPUT`
- `MCP_SERVER_REDACT_SENSITIVE_OUTPUT`
- `MCP_SERVER_OUTPUT_POLICY_MODE`
- `MCP_SERVER_SEARCH_RESULT_MODE`
- `MCP_SERVER_OPEN_URL_MODE`
- `MCP_SERVER_SUMMARY_MAX_CHARS`
- `MCP_SERVER_ALLOW_RAW_OUTPUT`

## 운영 권장값
- 기본 운영에서는 `MCP_SERVER_OUTPUT_POLICY_MODE=hybrid`
- 원문 노출이 필요할 때만 제한된 운영자 환경에서 `raw` 모드 사용
- `raw` 모드는 배포/점검 외 용도로는 가급적 사용하지 않음

## 확인 방법
1. `search_indexed_documents`를 호출해 `policy.mode`가 `masked_snippet`인지 확인
2. `search_web`를 호출해 `policy.summary_applied=true`가 찍히는지 확인
3. `open_urls`를 호출해 본문 전체가 아니라 짧은 요약이 내려오는지 확인
4. 응답 JSON의 `policy` 필드로 실제 적용 모드를 점검

## 111 서버 MCP 구동 주의사항
- 111은 MCP 서버를 개별 컨테이너로 띄운다
- `mcp_server/resources/document_sets.py`가 `get_accessible_document_sets()`를 요구한다
- 따라서 `utils.py`에는 문서 세트 조회 helper가 반드시 있어야 한다
- helper가 없으면 `mcp_server`가 import 단계에서 중단된다

## 점검 체크리스트
- [ ] `curl http://127.0.0.1:8090/health`가 `healthy`를 반환하는가
- [ ] `search_indexed_documents` 응답에 `policy`가 붙는가
- [ ] `search_web` 응답에 `policy.mode=masked_snippet` 및 `summary_applied=true`가 붙는가
- [ ] `open_urls` 응답에 `policy.mode=summary_only`가 붙는가
- [ ] 111 컨테이너에서 `get_accessible_document_sets` import 오류가 없는가

## 비고
- 이 문서는 MCP 출력 정책과 111 MCP 서버 구동 이슈를 함께 다루는 운영용 문서다.
- 코드 변경 시 이 문서와 `memory.md`를 함께 갱신한다.
