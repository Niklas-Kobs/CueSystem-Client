// Wartet, bis die Brücke zu Python (pywebview) steht
window.addEventListener('pywebviewready', function() {
    updateTable();
});

function updateTable() {
    window.pywebview.api.get_queue().then(function(response) {
        const tbody = document.getElementById('queueTableBody');
        tbody.innerHTML = ''; 

        response.forEach((patient, index) => {
            const isFirst = index === 0;
            const isLast = index === response.length - 1;

            const row = `<tr class="patient-row">
                            <td>${index + 1}</td>              
                            <td>${patient.patient_id}</td>      
                            <td>${patient.name}</td>
                            <td>${patient.room}</td>
                                <td class="action-cell">
                                    <div class="action-group">
                                        <button class="btn-main" onclick="moveItem(${index}, 'up')" ${isFirst ? 'disabled' : ''}>▲</button>
                                        <button class="btn-main" onclick="moveItem(${index}, 'down')" ${isLast ? 'disabled' : ''}>▼</button>
                                        <button class="btn-main" onclick="removeFromQueue(${index})">remove</button>
                                        <button class="btn-main" onclick="call(${index})">call</button>
                                        <button class="btn-2" onclick="openPopup(${index})">Ξ</button>
                                    </div>
                                </td>
                        </tr>`;
            tbody.innerHTML += row;
        });
    });
}

const popup = document.getElementById('POPUP');

function openPopup(index) {
    const popup = document.getElementById('POPUP');
    popup.showModal();

    window.pywebview.api.get_patient_details(index).then(response => {
        if (response) {
            document.getElementById('p_name_POP').value = response.name || '';
            document.getElementById('p_id_POP').value = response.patient_id || '';
            document.getElementById('p_room_POP').value = response.room || '';
            document.getElementById('p_infos_POP').value = response.infos || '';
            document.getElementById('p_doctor_POP').value = response.doctor || '';
            document.getElementById('p_duration_POP').value = response.duration || '0';
        } else {
            console.error("Patient nicht gefunden");
        }
    });
}

function closePopup() {
    popup.close();
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

    document.getElementById('p_name').value = '';
    document.getElementById('p_id').value = '';
    document.getElementById('p_room').value = '';
    document.getElementById('p_infos').value = '';
    document.getElementById('p_doctor').value = '';
    document.getElementById('p_duration').value = '0';
    document.getElementById('p_name').focus();
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
    let currentValue = parseInt(input.value) || 0;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0; // Verhindert Werte unter 1
    input.value = newValue;
}

function changeValue_duration_POP(delta) {
    const input = document.getElementById('p_duration_POP');
    let currentValue = parseInt(input.value) || 0;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0; // Verhindert Werte unter 1
    input.value = newValue;
}