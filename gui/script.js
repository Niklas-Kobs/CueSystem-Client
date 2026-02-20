// Wartet, bis die Brücke zu Python (pywebview) steht
window.addEventListener('pywebviewready', function() {
    updateTable();
});

function updateTable() {
    window.pywebview.api.get_queue().then(function(response) {
        const tbody = document.getElementById('queueTableBody');
        tbody.innerHTML = ''; 

        response.forEach((patient, index) => { // 'patient' ist jetzt ein Objekt
            const isFirst = index === 0;
            const isLast = index === response.length - 1;

            const row = `<tr>
                <td>${index + 1}</td>
                <td>${patient.patient_id}</td>
                <td>${patient.name}</td>
                <td>${patient.room}</td>
                <td>
                    <button class="btn-main" onclick="moveItem(${index}, 'up')" ${isFirst ? 'disabled' : ''}>▲</button>
                    <button class="btn-main" onclick="moveItem(${index}, 'down')" ${isLast ? 'disabled' : ''}>▼</button>
                    <button class="btn-main" onclick="removeFromQueue(${index})">remove</button>
                    <button class="btn-main" onclick="call(${index})">call</button>
                    <button class="btn-2" onclick="info(${index})">Ξ</button>
                </td>
            </tr>`;
            tbody.innerHTML += row;
        });
    });
}

function moveItem(index, direction) {
    window.pywebview.api.move_entry(index, direction).then(function() {
        updateTable();
    });
}

function addToQueue() {
    const data = {
    name: document.getElementById('p_name').value,
    id: document.getElementById('p_id').value,
    room: document.getElementById('p_room').value,
    infos: document.getElementById('p_infos').value,
    doctor: document.getElementById('p_doctor').value,
    duration: document.getElementById('p_duration').value
    };
    window.pywebview.api.add_full_patient(data).then(updateTable);
}

function removeFromQueue(index) {
    // Aufruf der Python-Funktion "remove_entry"
    window.pywebview.api.remove_entry(index).then(function() {
        updateTable();
    });
}

function changeValue_pos(delta) {
    const input = document.getElementById('p_pos');
    let currentValue = parseInt(input.value) || 1;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0; // Verhindert Werte unter 1
    input.value = newValue;
}
function changeValue_duration(delta) {
    const input = document.getElementById('p_duration');
    let currentValue = parseInt(input.value) || 1;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0; // Verhindert Werte unter 1
    input.value = newValue;
}