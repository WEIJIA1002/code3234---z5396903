function compareRegions() {
  const r1 = document.getElementById('region1-select').value;
  const r2 = document.getElementById('region2-select').value;
  const prefs = Array.from(document.querySelectorAll('#preferences input:checked')).map(i => i.value);

  const customFile = document.getElementById("customData").files[0];
  const formData = new FormData();
  formData.append("region1", r1);
  formData.append("region2", r2);
  formData.append("preferences", JSON.stringify(prefs));
  if (customFile) {
    formData.append("customFile", customFile);
  }

  fetch('/compare_regions', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById('ai-result').innerText = data.result || "AI Analysis Failed";
      if (data.regionPrices) {
        drawPriceChart(r1, r2, data.regionPrices);
      }
    });
}

let regionSelectionState = 1; // Used to alternate between setting Region 1 or Region 2

// // Create house SVG icon
const houseIcon = L.divIcon({
    className: 'custom-house-icon',
    html: `
      <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 64 64">
        <path d="M32 4 L4 28 H16 V60 H48 V28 H60 Z" fill="#90ee90" stroke="#2e8b57" stroke-width="2"/>
      </svg>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 26],
    popupAnchor: [0, -26]
});


// 初始化地图
const map = L.map('map').setView([-33.8688, 151.2093], 10); // 中心点为悉尼

// 添加基础图层
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// 加载 GeoJSON 边界数据
fetch('/static/data/nsw_cleaned_boundaries.geojson')
    .then(response => response.json())
    .then(data => {
        L.geoJSON(data, {
            style: {
                color: '#00008B',
                weight: 1,
                fillOpacity: 0.1
            },
            onEachFeature: function (feature, layer) {
                const bounds = layer.getBounds();
                const center = bounds.getCenter();
                const name = feature.properties.name || "Unknown Area";
            
                const marker = L.marker(center, { icon: houseIcon }).addTo(map);
                marker.bindPopup(`<strong>${name}</strong><br/><button onclick="selectRegion('${name}')">Select this region</button>`);
            
                layer.on({
                    mouseover: () => layer.setStyle({ weight: 2, fillOpacity: 0.3 }),
                    mouseout: () => layer.setStyle({ weight: 1, fillOpacity: 0.1 })
                });
            }
            
        }).addTo(map);
    })
    .catch(error => console.error("Failed to load GeoJSON:", error));
// ... existing code ...

function createChart(data) {
  const ctx = document.getElementById('chart').getContext('2d');
  const chart = new Chart(ctx, {
      type: 'bar', // 可以改为 'line' 或 'pie' 根据需要
      data: {
          labels: data.labels,
          datasets: [{
              label: 'Property Prices',
              data: data.values,
              backgroundColor: 'rgba(54, 162, 235, 0.2)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
          }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'price（$AUD）' // ✅ 设置 Y 轴单位
            }
          },
          x: {
            title: {
              display: true,
              text: 'Property type'
            }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function(ctx) {
                const label = ctx.dataset.label || '';
                const value = ctx.parsed.y || 0;
                return `${label}: $${value}`;
              }
            }
          }
        }
      }
    });
  }

document.addEventListener("DOMContentLoaded", () => {
    fetch("/init_data")
      .then(response => response.json())
      .then(data => {
        if (data.chartData) {
          document.getElementById("result").innerHTML = `<pre>${data.result}</pre>`;
          createChart(data.chartData);
        } else {
          document.getElementById("result").innerHTML = "⚠️ Failed to load data";
        }
      })
      .catch(error => console.error("Auto analysis loading failed:", error));
});


// 确保 DOM 完全加载完再运行
document.addEventListener("DOMContentLoaded", () => {
    fetch("/init_data")
      .then(response => response.json())
      .then(data => {
        if (data.chartData) {
          document.getElementById("result").innerHTML = `<pre>${data.result}</pre>`;
          createChart(data.chartData);
        } else {
          document.getElementById("result").innerHTML = "⚠️ Failed to load data";
        }
      })
      .catch(error => console.error("Auto analysis loading failed:", error));
  });
  
  function selectRegion(name) {
    const select1 = document.getElementById("region1-select");
    const select2 = document.getElementById("region2-select");

    if (regionSelectionState === 1) {
        select1.value = name;
        regionSelectionState = 2;
        alert(`Region 1 selected：${name}，please click the map to select Region 2`);
    } else {
        select2.value = name;
        regionSelectionState = 1;
        alert(`Region 2 selected：${name}，selection complete！`);
    }
}

function updateFileName() {
  const input = document.getElementById('customData');
  const fileName = input.files.length > 0 ? input.files[0].name : 'No file selected';
  document.getElementById('fileName').textContent = fileName;
}
