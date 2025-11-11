async function refreshDevices() {
  try {
    const res = await fetch('/api/devices');
    const data = await res.json();
    const tbody = document.getElementById('device-rows');
    tbody.innerHTML = '';
    Object.entries(data).forEach(([addr, d]) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${d.name}</td>
        <td>${addr}</td>
        <td>${d.status}</td>
        <td><a class="view-link" href="/device/${addr}">View</a></td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
  }
}
refreshDevices();
setInterval(refreshDevices, 5000);
