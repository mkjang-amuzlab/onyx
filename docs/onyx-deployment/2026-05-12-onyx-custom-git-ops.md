# 2026-05-12 Onyx Custom Git 운영 정리

## 목적
Onyx 원본 저장소를 직접 덮어쓰지 않고, 우리 수정본을 별도 `onyx_custom` 저장소로 관리한다. 수정된 파일 자체를 저장하고, 변경 이유와 운영 절차는 별도 문서로 남긴다.

## 합의한 운영 방식
- `upstream/main`: 원본 Onyx 추적용
- `origin/internal/main`: 우리 운영 기준 브랜치
- `origin/patch/<topic>`: 기능별 작업 브랜치
- `onyx_custom`에는 수정된 파일 자체를 저장한다.
- 원본 Onyx에 반영할 때는 overwrite가 아니라 git merge/rebase로 upstream 변경을 흡수한다.
- 배포 서버(246/111)는 `internal/main` 기준으로 동일하게 맞춘다.

## 저장소 구조
```text
onyx_custom/
  backend/
  deployment/
  docs/
  scripts/
```

- `backend/`: 실제 수정된 소스 파일
- `deployment/`: 배포/동기화 스크립트
- `docs/`: 변경 이유, 적용 절차, 롤백 방법
- `scripts/`: upstream 동기화 및 서버 반영 도구

## 동기화 절차
1. `git fetch upstream`
2. `git checkout internal/main`
3. `git rebase upstream/main` 또는 `git merge upstream/main`
4. 충돌 해결
5. `git push origin internal/main`
6. 246/111 서버에 동일 커밋 반영

## 운영 원칙
- 코드는 파일 자체로 보관한다.
- 변경 이유는 별도 문서로 남긴다.
- upstream 변경은 git merge/rebase로 흡수한다.
- 단순 덮어쓰기 방식은 사용하지 않는다.

## 다음 작업
- `onyx_custom`용 초기 디렉터리 구조 확정
- 변경 파일 목록 기준으로 커밋 단위 분리
- upstream 동기화 스크립트 초안 작성
- 서버 반영 스크립트 초안 작성
