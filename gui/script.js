window.addEventListener('pywebviewready', function() {
    detectChange();
    updateTable();
    alive();
});

let patientIndexToDelete = null;
let Change = false;
let originalRoom = "";

document.getElementById('remove_one').addEventListener('click', () => {
    if (patientIndexToDelete !== null) {
        removeFromQueue(patientIndexToDelete);
        document.getElementById('CONFIRM_DELETE_SINGLE_POP').close();
        patientIndexToDelete = null;
    }
});

document.getElementById('close_one').addEventListener('click', () => {
    document.getElementById('CONFIRM_DELETE_SINGLE_POP').close();
});

function updateTable() {
    window.pywebview.api.get_queue().then(function(response) {
        const tbody = document.getElementById('queueTableBody');
        tbody.innerHTML = ''; 

        response.forEach((patient, index) => {
            const isFirst = index === 0;
            const isLast = index === response.length - 1;
            
            const callClass = patient.is_called === 1 ? 'call' : '';

            const row = `<tr class="patient-row ${callClass}" data-index="${index}">
                            <td>${index + 1}</td>              
                            <td>${patient.patient_id}</td>
                            <td>${patient.name}</td>
                            <td>${patient.room}</td>
                            <td class="action-cell">
                                <div class="action-group">
                                    <button class="btn-main" data-tooltip="Moves the patient one position up" onclick="moveItem(${index}, 'up')" ${isFirst ? 'disabled' : ''}>▲</button>
                                    <button class="btn-main" data-tooltip="Moves the patient one position down" onclick="moveItem(${index}, 'down')" ${isLast ? 'disabled' : ''}>▼</button>
                                    <button class="btn-main" data-tooltip="Delete Patient" onclick="openRemoveSingle(${index})">remove</button>
                                    <button class="btn-main" data-tooltip="Call Patient" onclick="call(${index})">call</button>
                                    <button class="btn-2" data-tooltip="Open Patient Information" onclick="openPopup(${index})">Ξ</button>
                                    <button class="btn-2" data-tooltip="Move Patient to Top" onclick="moveToTop(${index})">↑</button>
                                    <button class="btn-2" data-tooltip="Move Patient to Bottom" onclick="sendToEnd(${index})">↓</button>
                                </div>
                            </td>
                        </tr>`;
            tbody.innerHTML += row;
        });
    });
}

function addToPos() {
    const posInput = document.getElementById('p_pos');
    const targetIndex = Math.max(0, (parseInt(posInput.value) || 1) - 1);

    const data = {
        name: document.getElementById('p_name').value,
        id: document.getElementById('p_id').value,
        room: document.getElementById('p_room').value,
        infos: document.getElementById('p_infos').value,
        doctor: document.getElementById('p_doctor').value,
        duration: document.getElementById('p_duration').value
    };
    if (!data.name || !data.id) {
        document.getElementById('Headline_alert').innerText = 'Ups!';
        document.getElementById('Message_alert').innerText = 'Bitte füllen Sie mindestens die Felder "Name" und "ID" aus.';
        openAlert_Popup();
        return;
    }
    else{Change = true}
    window.pywebview.api.add_at_position(data, targetIndex).then(success => {
        if (success) {
            updateTable();
            document.getElementById('p_name').value = '';
            document.getElementById('p_id').value = '';
            document.getElementById('p_room').value = '';
            document.getElementById('p_infos').value = '';
            document.getElementById('p_doctor').value = '';
            document.getElementById('p_duration').value = '0';
            posInput.value = '1';
            document.getElementById('p_name').focus();
        }
    });
}

const popup = document.getElementById('POPUP');

let currentEditId = null;

function openPopup(index) {
    const popup = document.getElementById('POPUP');
    popup.showModal();
    window.pywebview.api.get_patient_details(index).then(response => {
        if (response) {
            currentEditId = response.id;
            document.getElementById('p_name_POP').value = response.name;
            document.getElementById('p_id_POP').value = response.patient_id;
            document.getElementById('p_room_POP').value = response.room;
            document.getElementById('p_infos_POP').value = response.infos;
            document.getElementById('p_doctor_POP').value = response.doctor;
            document.getElementById('p_duration_POP').value = response.duration;
            const durElement = document.getElementById('p_room_POP');
            originalRoom = durElement.value.toString().trim();
        }
    });
}

function openPopup_Opt() {
    const popup_opt = document.getElementById('POPUP_Option');
    popup_opt.showModal();
}

function closePopup() {
    popup.close();
}

function closePopup_Opt() {
    const popup_opt = document.getElementById('POPUP_Option');
    if (popup_opt) {
        popup_opt.close();
    }
}


function clearAll() {
    const confirmPopup = document.getElementById('CONFIRM_DELETE_POP');
    confirmPopup.showModal();
}

function openRemoveSingle(index){
    patientIndexToDelete = index;
    const confirmremovePopup = document.getElementById('CONFIRM_DELETE_SINGLE_POP');
    confirmremovePopup.showModal();
}

function closeConfirmPopup() {
    document.getElementById('CONFIRM_DELETE_POP').close();
}


function executeClearAll() {
    Change = true
    window.pywebview.api.clear_all_entries().then(success => {
        if (success) {
            updateTable();
            closeConfirmPopup(); 

            const optPopup = document.getElementById('POPUP_Option');
            if (optPopup) optPopup.close();
        }
    });
}

function call(index) {
    Change = true
    if (index <=4) {
    window.pywebview.api.toggle_call_status(index).then(success => {
        if (success) {
            updateTable();
        }
    });
    } else {
        document.getElementById('Headline_alert').innerText = 'Ups!';
        document.getElementById('Message_alert').innerText = 'Es können nur die ersten 5 Patienten angerufen werden.';
        openAlert_Popup();
        return;
    }
}

function savePopup() {

    const currentRoom = document.getElementById('p_room_POP').value.toString().trim();

    const updatedData = {
        id: currentEditId,
        name: document.getElementById('p_name_POP').value,
        patient_id: document.getElementById('p_id_POP').value,
        room: document.getElementById('p_room_POP').value,
        infos: document.getElementById('p_infos_POP').value,
        doctor: document.getElementById('p_doctor_POP').value,
        duration: document.getElementById('p_duration_POP').value
    };

    window.pywebview.api.save_patient_edit(updatedData).then(success => {
        if (success) {
            document.getElementById('POPUP').close();
            updateTable();
        }
    });

    if (originalRoom !== currentRoom) {
        Change = true;
    }
}

function moveItem(index, direction) {
    Change = true
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
    if (!data.name || !data.id) {
        document.getElementById('Headline_alert').innerText = 'Ups!';
        document.getElementById('Message_alert').innerText = 'Bitte füllen Sie mindestens die Felder "Name" und "ID" aus.';
        openAlert_Popup();
        return;
    }
    else {Change = true}
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
    Change = true
    window.pywebview.api.remove_entry(index).then(function() {
        updateTable();
    });
}

function changeValue_pos(delta) {
    const input = document.getElementById('p_pos');
    let currentValue = parseInt(input.value) || 1;
    let newValue = currentValue + delta;
    
    if (newValue < 1) newValue = 1; 
    input.value = newValue;
}
function changeValue_duration(delta) {
    const input = document.getElementById('p_duration');
    let currentValue = parseInt(input.value) || 0;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0;
    input.value = newValue;
}

function changeValue_duration_POP(delta) {
    const input = document.getElementById('p_duration_POP');
    let currentValue = parseInt(input.value) || 0;
    let newValue = currentValue + delta;
    
    if (newValue < 0) newValue = 0;
    input.value = newValue;
}

function openAlert_Popup(){
    const alertPopup = document.getElementById('Alert_POP');
    alertPopup.showModal();
}

function closeAlert_Popup(){
    const alertPopup = document.getElementById('Alert_POP');
    alertPopup.close();
}

function openQueueinBrowser() {
    window.pywebview.api.open_external_link('http://192.168.0.200:55000/');
}

function openQueue() {
    const frame = document.getElementById('api_frame');
    const popup = document.getElementById('POPUP_Web');
    
    frame.src = "http://192.168.0.200:55000/"; 
    popup.showModal();
}

function closeWebPopup() {
    const frame = document.getElementById('api_frame');
    const popup = document.getElementById('POPUP_Web');
    
    popup.close();
    frame.src = "about:blank";
}

function applyTemplate() {
    const templateSelect = document.getElementById('p_template');
    const subjectField = document.getElementById('m_title');
    const messageField = document.getElementById('m_text');

    const templates = {
        "none": {
            subject: "",
            text: ""
        },
        "Patient": {
            subject: "Der Patient mit der Nummer: #",
            text: "Nachricht"
        },
        "Notfall": {
            subject: "!!Achtung!!",
            text: "Aufgrund einer Technischenstörung in der Gebäudetechnik bitten wir sie die Praxis zu verlassen. Bitte halten sie sich an die Anweisungen des Personals"
        },
        "QueueDefekt": {
            subject: "Technische Störung",
            text: "Die Warteslange steht gerade nicht zur Verfügung. Bitte achten sie auf die Ansagen des Personals"
        }
    };
    const selectedValue = templateSelect.value;

    if (templates[selectedValue]) {
        subjectField.value = templates[selectedValue].subject;
        messageField.value = templates[selectedValue].text;
    }
}

function refresh() {
    Change = false
    window.pywebview.api.refresh().then(function(response) {
        if (response) {
            closePopup_Opt();
    }});
}

function Call_6() {
    window.pywebview.api.Call_6();
}

function sndMsg() {
    const subject = document.getElementById('m_title').value;
    const message = document.getElementById('m_text').value;
    window.pywebview.api.send_message(subject, message);
}

function removeMsg() {
    const subject = 'remove';
    const message = '---';
    window.pywebview.api.send_message(subject, message);
}

function sendToEnd(index) {
    Change = true
    window.pywebview.api.move_to_end(index).then(success => {
        if (success) {
            updateTable();
        }
    });
}

function moveToTop(Index) {
    Change = true
        window.pywebview.api.move_to_top(Index).then(success => {
            if (success) {
                updateTable();
            }
        });
}

function detectChange() {
    if (Change === true){
        document.getElementById('refresh-btn').classList.add('Change');
    }
    else {
        document.getElementById('refresh-btn').classList.remove('Change');
    }
    setTimeout(detectChange, 200);
}

function alive() {
    const WarningPop = document.getElementById('Alert_POP')
    window.pywebview.api.alive().then(success => {
        if (success) {
            document.getElementById('alive-btn').classList.remove('Alive');
        }
        else {
            document.getElementById('alive-btn').classList.add('Alive');
            document.getElementById('Headline_alert').innerText = 'Ups!';
            document.getElementById('Message_alert').innerText = 'Die Public Queue ist offline. Bitte starte den Server oder wende dich an den IT Support';
            openAlert_Popup();
        }
    });
    setTimeout(alive, 10000);
}