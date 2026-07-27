# 29초영화제 결과보고서 도우미

## 현재 구현된 MVP 기반

- Windows 기본 GUI
- 결과보고 프로젝트 경로 입력·선택
- 제작 중·최종 결과보고서 제외 자료 스캔
- 29초영화제·29역숏폼왕 유형 감지
- 보고서 영역별 자료 준비도 표시
- 표준 결과보고 폴더 ZIP 생성
- 선택한 위치에 표준 폴더 직접 생성
- 최근 자료점검 JSON 저장

## 실행

```powershell
python run_app.py
```

## 테스트

```powershell
python -m unittest discover -s tests -v
```

## 다음 구현

1. 프로젝트 입력 데이터와 Excel 양방향 동기화
2. 문서·리포트 정보 추출
3. 누락·불일치 검증
4. 신한 PPTX 템플릿 엔진
5. AI 총평 초안
6. PowerPoint PDF 변환과 NAS 최종 저장
