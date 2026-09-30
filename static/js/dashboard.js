(function () {
  const readData = (id) => {
    const node = document.getElementById(id);
    return node ? JSON.parse(node.textContent) : [];
  };
  const ages = readData("age-data");
  const targets = readData("target-data");
  const palette = { green: "#147d72", coral: "#d45e4b", blue: "#4d8292", yellow: "#c58e2f" };
  const common = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } };
  const ageCanvas = document.getElementById("ageChart");
  if (ageCanvas) {
    new Chart(ageCanvas, {
      type: "scatter",
      data: { datasets: [
        { label: "Lower risk", data: ages.filter((_, i) => targets[i] === 0).map((age, i) => ({ x: age, y: i + 1 })), backgroundColor: palette.green },
        { label: "Elevated risk", data: ages.filter((_, i) => targets[i] === 1).map((age, i) => ({ x: age, y: i + 1 })), backgroundColor: palette.coral }
      ] },
      options: { ...common, scales: { x: { title: { display: true, text: "Age (years)" }, min: 18 }, y: { display: false, min: 0 } }, plugins: { legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 7, font: { size: 10 } } } } }
    });
  }
  const genderCanvas = document.getElementById("genderChart");
  if (genderCanvas) new Chart(genderCanvas, { type: "doughnut", data: { labels: readData("gender-labels"), datasets: [{ data: readData("gender-values"), backgroundColor: [palette.green, palette.blue], borderWidth: 0 }] }, options: { ...common, cutout: "68%", plugins: { legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 7, font: { size: 10 } } } } } });
  const cholesterolCanvas = document.getElementById("cholesterolChart");
  if (cholesterolCanvas) new Chart(cholesterolCanvas, { type: "bar", data: { labels: readData("cholesterol-labels"), datasets: [{ data: readData("cholesterol-values"), backgroundColor: palette.blue, borderRadius: 3 }] }, options: { ...common, scales: { x: { title: { display: true, text: "mg/dL" }, grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0 } } } } });
  const outcomeCanvas = document.getElementById("outcomeChart");
  if (outcomeCanvas) new Chart(outcomeCanvas, { type: "doughnut", data: { labels: ["Lower risk", "Elevated risk"], datasets: [{ data: [targets.filter((v) => v === 0).length, targets.filter((v) => v === 1).length], backgroundColor: [palette.green, palette.coral], borderWidth: 0 }] }, options: { ...common, cutout: "68%", plugins: { legend: { display: true, position: "bottom", labels: { usePointStyle: true, boxWidth: 7, font: { size: 10 } } } } } });
})();