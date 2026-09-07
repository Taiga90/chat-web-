const socket = io();

// --------- 全体チャット ---------
socket.on("message", (data) => {
    if (typeof room !== "undefined") return;
    if (typeof room_id !== "undefined") return;

    const box = document.createElement("div");
    box.classList.add("message-box");
    if (data.user === username) box.classList.add("message-self");

    box.textContent = data.user + ": " + data.text;
    document.getElementById("messages").appendChild(box);
});

function sendMsg() {
    const text = document.getElementById("msg").value;
    socket.send({ user: username, text: text });
    document.getElementById("msg").value = "";
}

// --------- DM ---------
if (typeof room_id !== "undefined") {
    socket.emit("join_dm", { room_id });

    socket.on("dm_message", (data) => {
        const box = document.createElement("div");
        box.classList.add("message-box");
        if (data.user === username) box.classList.add("message-self");

        box.textContent = data.user + ": " + data.text;
        document.getElementById("messages").appendChild(box);
    });
}

function sendDm() {
    const text = document.getElementById("msg").value;
    socket.emit("dm_message", {
        room_id,
        user: username,
        text
    });
    document.getElementById("msg").value = "";
}

// --------- チャットルーム ---------
if (typeof room !== "undefined") {
    socket.emit("join_room", { room });

    socket.on("room_message", (data) => {
        const box = document.createElement("div");
        box.classList.add("message-box");
        if (data.user === username) box.classList.add("message-self");

        box.textContent = data.user + ": " + data.text;
        document.getElementById("messages").appendChild(box);
    });
}

function sendRoom() {
    const text = document.getElementById("msg").value;
    socket.emit("room_message", {
        room,
        user: username,
        text
    });
    document.getElementById("msg").value = "";
}
