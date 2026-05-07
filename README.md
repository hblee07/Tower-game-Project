# Tower-game-Project
고컴 게임 프로젝트

Project_Root/
│
├── main.py                # 게임 실행 진입점 (Game Loop)
├── settings.py            # 화면 크기, 색상, 타워 가격, 스탯 등 상수 관리
│
├── 📁 models/             # 게임 객체 클래스
│   ├── tower.py           # Tower(부모), BowTower, CannonTower, IceTower
│   ├── enemy.py           # Enemy(부모), Goblin, Orc, Troll
│   └── projectile.py      # 화살, 대포알 등 발사체
│
├── 📁 systems/           # 시스템 로직
│   ├── map_manager.py     # 30x30 격자 생성 및 A* 알고리즘
│   ├── wave_manager.py    # 웨이브 데이터 및 스폰 로직
│   ├── economy.py         # 골드 및 점수 계산
│   └── save_manager.py    # JSON을 이용한 세이브/로드 및 랭킹
│
├── 📁 UI/                 # 화면 표시
│   ├── HUD.py             # 상단 정보 바, 버튼
│   └── screens.py         # 타이틀, 게임오버, 랭킹 화면
│
└── 📁 assets/             # 이미지 및 사운드 리소스