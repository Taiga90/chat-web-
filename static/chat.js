const socket = io();

socket.on("message", (data) => {
    const box = document.createElement("div");
    box.classList.add("message-box");

    if (data.user === username) {
        box.classList.add("message-self");
    }

    box.textContent = data.user + ": " + data.text;
    document.getElementById("messages").appendChild(box);
});

function sendMsg() {
    const text = document.getElementById("msg").value;
    socket.send({ user: username, text: text });
    document.getElementById("msg").value = "";
}
