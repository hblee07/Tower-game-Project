# Tower-game-Project
고컴 게임 프로젝트

Project_Root/
│
├── main.py                # 게임 실행 진입점 (Game Loop 및 화면 업데이트)
├── settings.py            # 화면 크기, 색상, 타워 가격, 스탯 등 전역변수 관리
│
├── 📁 models/             # 게임 내 살아 숨쉬는 객체들 (데이터+행동)
│   ├── __init__.py        
│   ├── tower.py           # Tower(부모), BowTower, CannonTower, IceTower
│   ├── enemy.py           # Enemy(부모), Goblin, Orc, Troll
│   ├── projectile.py      # 화살, 대포알 등 발사체
│   └── effect.py          # 폭발, 감전, 타격 이펙트 등 시각 효과
│
├── 📁 systems/            # 보이지 않는 곳에서 돌아가는 게임 로직
│   ├── __init__.py
│   ├── scenes.py          # 화면 전환(타이틀->게임), 게임 오버 상태 등 전반적 흐름 제어
│   ├── map.py             # 30x30 격자 생성 및 A* 알고리즘 (경로 계산)
│   ├── wave.py            # 웨이브 데이터 및 스폰 로직
│   ├── economy.py         # 골드, 플레이어 체력(성), 점수 계산
│   └── save.py            # JSON을 이용한 세이브/로드 및 랭킹
│
├── 📁 ui/                 # UI 표시 및 사용자 입력
│   ├── __init__.py
│   ├── hud.py             # 상단 정보 바, 타워 건설 버튼 모음
│   └── screens.py         # 타이틀, 게임오버, 랭킹 등 전체 화면 단위
│
└── 📁 assets/             # 이미지, 사운드, 폰트, JSON 데이터 등
    ├── images/
    └── sounds/