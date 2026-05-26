# Tower Defense

## 조작
# 타워 버튼 클릭 후 빈 칸 클릭: 설치
# 타워 클릭: 선택 및 공격 범위 표시
# M: 선택한 타워를 merge source로 지정한 뒤 같은 종류/레벨 타워 클릭
# U: 업그레이드
# Space: 스킬
# Delete: 판매
# S: 저장
# P 또는 ESC: 일시정지

## 구현된 요구사항 요약
# 30x30 grid map, BFS pathfinding, path blocking prevention
# 2 playable stages
# 4 tower types: bomb, lightning, thorn, random
# max merge level 3, max upgrade level 5
# projectile/effect rendering
# 3 normal enemy types and boss with regeneration ability
# 5 waves, boss appears every wave
# gold, castle HP, wave HUD
# title/game/end/ranking scenes
# save/continue and persistent ranking
# generated looping BGM with safe fallback
