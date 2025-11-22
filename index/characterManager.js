// 1. 캐릭터 이미지 경로 설정 (레벨 1~5)
const CHAR_IMAGES = {
  1: "./image/seed.png",      // 1단계: 씨앗
  2: "./image/Lv2smile.png",    // 2단계: 새싹 (이미지명 수정하세요)
  3: "./image/Lv3smile.png",    // 3단계: 꽃 (이미지명 수정하세요)
  4: "./image/Lv4smile.png",      // 4단계: 나무 (이미지명 수정하세요)
  5: "./image/Lv5smile.png"     // 5단계: 숲 (이미지명 수정하세요)
};

// 2. 현재 레벨 가져오기 (저장된 게 없으면 기본 1)
function getCurrentLevel() {
  const savedLevel = localStorage.getItem('userLevel');
  return savedLevel ? parseInt(savedLevel) : 1;
}

// 3. 레벨 저장하기 (강제로 레벨을 바꿀 때 사용)
function setLevel(newLevel) {
  if (newLevel < 1) newLevel = 1;
  if (newLevel > 5) newLevel = 5;
  
  localStorage.setItem('userLevel', newLevel);
  updateCharacterImage(); // 저장 즉시 이미지도 변경
}

// 4. 화면에 있는 캐릭터 이미지를 찾아 자동으로 바꾸는 함수
function updateCharacterImage() {
  const level = getCurrentLevel();
  const imageUrl = CHAR_IMAGES[level];

  // 화면에서 캐릭터 이미지 태그들을 다 찾아서 바꿔치기
  const charImages = document.querySelectorAll('.character-img, .char-img, .mascot-img');
  
  charImages.forEach(img => {
    img.src = imageUrl;
  });

  // 레벨 텍스트(Lv. 1 등)도 있다면 바꿈
  const levelTexts = document.querySelectorAll('.level-text');
  levelTexts.forEach(text => {
    text.innerText = `Lv. ${level}`;
  });
}

// ▼▼▼ [수정됨] 5. 현실적인 레벨 기준 로직 ▼▼▼
function setLevelByRegret(regretRate) {
  let newLevel = 1;

  // === 🏆 현실적인 밸런스 패치 ===
  // 만족(후회 안함)이 절반은 넘어야 꽃(Lv3)은 유지하게 설정
  
  if (regretRate <= 15) {
    newLevel = 5; // 0~15% : 거의 완벽함 (숲)
  } else if (regretRate <= 35) {
    newLevel = 4; // 16~35% : 훌륭함 (나무)
  } else if (regretRate <= 55) {
    newLevel = 3; // 36~55% : 딱 반반, 주의 필요 (꽃)
  } else if (regretRate <= 75) {
    newLevel = 2; // 56~75% : 후회가 더 많음 (새싹)
  } else {
    newLevel = 1; // 76%~   : 습관 개선 시급 (씨앗)
  }
  // ===========================

  console.log(`현재 후회율 ${regretRate}% -> 레벨 ${newLevel}로 설정됨`);
  setLevel(newLevel); // 계산된 레벨로 저장
}

// 6. 페이지가 로딩되면 자동으로 캐릭터 업데이트 실행
document.addEventListener('DOMContentLoaded', () => {
  updateCharacterImage();
});