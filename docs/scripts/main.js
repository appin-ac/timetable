// すべてのデータをここに集約（親カテゴリ名、子要素の表示名とURL）
const data = [
  {
    category: "日豊本線宮崎駅",
    items: [
      { text: "2016", url: "../miyazaki_a/2016.html" },
      { text: "2019", url: "../miyazaki_a/2019.html" },
      { text: "2020", url: "../miyazaki_a/2020.html" },
      { text: "2022", url: "../miyazaki_a/2022.html" },
      { text: "2024", url: "../miyazaki_a/2024.html" },
      { text: "2025", url: "../miyazaki_a/2025.html" },
      { text: "2026", url: "../miyazaki_a/2026.html" }
    ]
  },
  {
    category: "日南線",
    items: [
      { text: "2016", url: "../nichinan/2016.html" },
      { text: "2019", url: "../nichinan/2019.html" },
      { text: "2026", url: "../nichinan/2026.html" }
    ]
  }
];

const mainSelect = document.getElementById("category");
const subSelect = document.getElementById("subCategory");
const submitBtn = document.getElementById("submitBtn");

// 初期化：1つ目のプルダウンを生成
function init() {
  mainSelect.innerHTML = '<option value="">路線・駅を選択</option>';
  subSelect.innerHTML = '<option value="">年を選択</option>';
  
  data.forEach((group, index) => {
    const option = document.createElement("option");
    option.value = index; // 配列のインデックスを値にする
    option.textContent = group.category;
    mainSelect.appendChild(option);
  });
}

// 1つ目が変更された時の処理
mainSelect.addEventListener("change", function() {
  subSelect.innerHTML = '<option value="">年を選択</option>';
  const selectedIndex = this.value;

  if (selectedIndex !== "") {
    const items = data[selectedIndex].items;
    items.forEach(item => {
      const option = document.createElement("option");
      option.value = item.url;
      option.textContent = item.text;
      subSelect.appendChild(option);
    });
    subSelect.disabled = false;
  } else {
    subSelect.disabled = true;
  }
});

// 2つ目のプルダウン変更時（ボタンの活性化のみ行う）
subSelect.addEventListener("change", function() {
  if (this.value) {
    submitBtn.disabled = false; // 正常な値が選ばれたらボタンを押せるようにする
  } else {
    submitBtn.disabled = true;
  }
});

// 確定ボタン押下時（ここで初めてページ遷移）
submitBtn.addEventListener("click", function() {
  const url = subSelect.value;
  if (url) {
    location.href = url;
  }
});

// 実行
init();