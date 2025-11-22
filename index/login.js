// script.js

document.addEventListener("DOMContentLoaded", () => {
  const kakaoLoginButton = document.getElementById("kakao-login");
  if (!kakaoLoginButton) return;

  kakaoLoginButton.addEventListener("click", () => {
    // TODO: 실제 카카오 로그인 URL로 교체
    // 예시:
    // const kakaoLoginUrl =
    //   "https://kauth.kakao.com/oauth/authorize?client_id=...&redirect_uri=...&response_type=code";

    const kakaoLoginUrl = "#";

    if (kakaoLoginUrl === "#") {
      console.log("kakaoLoginUrl을 실제 카카오 로그인 주소로 교체하세요.");
      return;
    }

    window.location.href = kakaoLoginUrl;
  });
});
