const socket = io();

// --------- 全体チャット用 ---------
socket.on("message", (data) => {
    if (typeof room_id !== "undefined") return; // DM画面では無視

    const box = document.createElement("div");
    box.classList.add("message-box");

    if (data.user === username) {
        box.classList.add("message-self");
    }

    box.textContent = data.user + ": " + data.text;
    document.getElementById("messages").appendChild(box);
});

socket.on("image", (data) => {
    if (typeof room_id !== "undefined") return; // DM画面では無視

    const box = document.createElement("div");
    box.classList.add("message-box");

    if (data.user === username) {
        box.classList.add("message-self");
    }

    const img = document.createElement("img");
    img.src = data.url;
    img.classList.add("message-image");

    box.appendChild(img);
    document.getElementById("messages").appendChild(box);
});

function sendMsg() {
    const text = document.getElementById("msg").value;
    socket.send({ user: username, text: text });
    document.getElementById("msg").value = "";
}

// --------- DM用 ---------
if (typeof room_id !== "undefined") {
    socket.emit("join_dm", { room_id: room_id });

    socket.on("dm_message", (data) => {
        const box = document.createElement("div");
        box.classList.add("message-box");

        if (data.user === username) {
            box.classList.add("message-self");
        }

        box.textContent = data.user + ": " + data.text;
        document.getElementById("messages").appendChild(box);
    });
}

function sendDm() {
    const text = document.getElementById("msg").value;
    socket.emit("dm_message", {
        room_id: room_id,
        user: username,
        text: text
    });
    document.getElementById("msg").value = "";
}
