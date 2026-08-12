const chat = document.getElementById("chat");
const messageInput = document.getElementById("message");
const sendButton = document.getElementById("send");

const activity = document.getElementById("activity");

const chatList = document.getElementById("chat-list");
const pinnedList = document.getElementById("pinned-list");
const pinnedSection =
    document.getElementById("pinned-section");

const newChatButton =
    document.getElementById("new-chat");

const currentChatTitle =
    document.getElementById("current-chat-title");

const chatMenu =
    document.getElementById("chat-menu");

const pinChatButton =
    document.getElementById("pin-chat");

const renameChatButton =
    document.getElementById("rename-chat");

const shareChatButton =
    document.getElementById("share-chat");

const deleteChatButton =
    document.getElementById("delete-chat");

const settingsButton =
    document.getElementById("settings-button");

const settingsModal =
    document.getElementById("settings-modal");

const closeSettingsButton =
    document.getElementById("close-settings");

const saveSettingsButton =
    document.getElementById("save-settings");

const userNameInput =
    document.getElementById("user-name");

const languageSelect =
    document.getElementById("language");

const confirmation =
    document.getElementById("confirmation");

const confirmationTool =
    document.getElementById("confirmation-tool");

const confirmationArgs =
    document.getElementById("confirmation-args");

const allowButton =
    document.getElementById("allow");

const denyButton =
    document.getElementById("deny");


/* ==========================================================
   STATE
   ========================================================== */

let chats = [];

let currentChatId = null;

let currentJob = null;

let menuChatId = null;


/* ==========================================================
   STORAGE
   ========================================================== */

const CHAT_STORAGE =
    "dmc_chat_history_v2";

const SETTINGS_STORAGE =
    "dmc_user_settings_v1";


let settings = {

    name: "",

    language: "de"
};


/* ==========================================================
   IDS
   ========================================================== */

function generateId() {

    return (
        Date.now().toString(36) +
        "_" +
        Math.random()
            .toString(36)
            .substring(2, 10)
    );
}


/* ==========================================================
   CHAT STORAGE
   ========================================================== */

function saveChats() {

    localStorage.setItem(
        CHAT_STORAGE,
        JSON.stringify(chats)
    );
}


function loadChats() {

    try {

        const stored =
            localStorage.getItem(
                CHAT_STORAGE
            );

        if (!stored) {

            chats = [];

            return;
        }

        const parsed =
            JSON.parse(stored);

        chats =
            Array.isArray(parsed)
                ? parsed
                : [];

    } catch {

        chats = [];
    }
}


/* ==========================================================
   SETTINGS STORAGE
   ========================================================== */

function saveSettings() {

    localStorage.setItem(
        SETTINGS_STORAGE,
        JSON.stringify(settings)
    );
}


function loadSettings() {

    try {

        const stored =
            localStorage.getItem(
                SETTINGS_STORAGE
            );

        if (!stored) {
            return;
        }

        const parsed =
            JSON.parse(stored);

        if (parsed.name) {

            settings.name =
                parsed.name;
        }

        if (parsed.language) {

            settings.language =
                parsed.language;
        }

    } catch {

        console.log(
            "DMC: Settings could not be loaded."
        );
    }
}


function applySettingsToUI() {

    userNameInput.value =
        settings.name || "";

    languageSelect.value =
        settings.language || "de";
}


/* ==========================================================
   CHAT CREATION
   ========================================================== */

function createChat() {

    const newChat = {

        id: generateId(),

        title: "NEW CHAT",

        created: Date.now(),

        updated: Date.now(),

        pinned: false,

        messages: []
    };


    chats.unshift(
        newChat
    );


    currentChatId =
        newChat.id;


    saveChats();

    renderChatList();

    renderCurrentChat();

    messageInput.focus();
}


/* ==========================================================
   CURRENT CHAT
   ========================================================== */

function getCurrentChat() {

    return chats.find(
        item =>
            item.id ===
            currentChatId
    );
}


/* ==========================================================
   TITLE
   ========================================================== */

function generateTitle(text) {

    let title =
        text
            .replace(/\s+/g, " ")
            .trim();


    if (!title) {

        return "NEW CHAT";
    }


    if (title.length > 40) {

        title =
            title.substring(
                0,
                40
            ) + "…";
    }


    return title;
}


/* ==========================================================
   CHAT LIST
   ========================================================== */

function renderChatList() {

    chatList.innerHTML = "";

    pinnedList.innerHTML = "";


    chats.sort(
        (a, b) =>
            (b.updated || 0) -
            (a.updated || 0)
    );


    const pinned =
        chats.filter(
            chat => chat.pinned
        );


    const normal =
        chats.filter(
            chat => !chat.pinned
        );


    /* PINNED */

    if (pinned.length > 0) {

        pinnedSection.classList.remove(
            "hidden"
        );

        pinned.forEach(
            chat => {

                pinnedList.appendChild(
                    createChatElement(chat)
                );
            }
        );

    } else {

        pinnedSection.classList.add(
            "hidden"
        );
    }


    /* NORMAL */

    if (normal.length === 0) {

        const empty =
            document.createElement(
                "div"
            );

        empty.style.padding =
            "15px 12px";

        empty.style.color =
            "#444";

        empty.style.fontSize =
            "10px";

        empty.textContent =
            "NO CHATS YET";

        chatList.appendChild(
            empty
        );

    } else {

        normal.forEach(
            chat => {

                chatList.appendChild(
                    createChatElement(chat)
                );
            }
        );
    }
}


/* ==========================================================
   CHAT ELEMENT
   ========================================================== */

function createChatElement(chatData) {

    const element =
        document.createElement(
            "div"
        );

    element.className =
        "chat-item";


    if (
        chatData.id ===
        currentChatId
    ) {

        element.classList.add(
            "active"
        );
    }


    if (chatData.pinned) {

        const pin =
            document.createElement(
                "span"
            );

        pin.className =
            "chat-item-pin";

        pin.textContent =
            "●";

        element.appendChild(
            pin
        );
    }


    const title =
        document.createElement(
            "div"
        );

    title.className =
        "chat-item-title";

    title.textContent =
        chatData.title ||
        "NEW CHAT";


    const menuButton =
        document.createElement(
            "button"
        );

    menuButton.className =
        "chat-menu-button";

    menuButton.textContent =
        "•••";


    menuButton.addEventListener(
        "click",
        event => {

            event.stopPropagation();

            openChatMenu(
                chatData.id,
                event
            );
        }
    );


    element.appendChild(
        title
    );

    element.appendChild(
        menuButton
    );


    element.addEventListener(
        "click",
        () => {

            openChat(
                chatData.id
            );
        }
    );


    return element;
}


/* ==========================================================
   OPEN CHAT
   ========================================================== */

function openChat(id) {

    const target =
        chats.find(
            chat =>
                chat.id === id
        );


    if (!target) {
        return;
    }


    currentChatId =
        id;


    closeChatMenu();

    renderChatList();

    renderCurrentChat();

    messageInput.focus();
}


/* ==========================================================
   RENDER CURRENT CHAT
   ========================================================== */

function renderCurrentChat() {

    chat.innerHTML = "";

    activity.innerHTML = "";


    const current =
        getCurrentChat();


    if (!current) {

        currentChatTitle.textContent =
            "NEW CHAT";

        return;
    }


    currentChatTitle.textContent =
        current.title;


    if (
        !current.messages ||
        current.messages.length === 0
    ) {

        addInitialMessage();

        return;
    }


    current.messages.forEach(
        message => {

            addMessageToDOM(
                message.sender,
                message.text,
                message.type
            );
        }
    );


    setTimeout(
        () => {

            chat.scrollTop =
                chat.scrollHeight;

        },
        0
    );
}


/* ==========================================================
   INITIAL MESSAGE
   ========================================================== */

function addInitialMessage() {

    addMessageToDOM(

        "DMC",

        "System online.\n\nWhat do you want me to do?",

        "dmc"
    );
}


/* ==========================================================
   MESSAGE DOM
   ========================================================== */

function addMessageToDOM(
    sender,
    text,
    type
) {

    const wrapper =
        document.createElement(
            "div"
        );

    wrapper.className =
        `message ${type}-message`;


    const label =
        document.createElement(
            "div"
        );

    label.className =
        "message-label";

    label.textContent =
        sender;


    const content =
        document.createElement(
            "div"
        );

    content.className =
        "message-content";

    content.textContent =
        text;


    wrapper.appendChild(
        label
    );

    wrapper.appendChild(
        content
    );


    chat.appendChild(
        wrapper
    );
}


/* ==========================================================
   SAVE MESSAGE
   ========================================================== */

function saveMessage(
    sender,
    text,
    type
) {

    const current =
        getCurrentChat();


    if (!current) {
        return;
    }


    if (!current.messages) {

        current.messages = [];
    }


    current.messages.push({

        sender,

        text,

        type,

        timestamp:
            Date.now()
    });


    current.updated =
        Date.now();


    saveChats();

    renderChatList();
}


/* ==========================================================
   ADD MESSAGE
   ========================================================== */

function addMessage(
    sender,
    text,
    type
) {

    addMessageToDOM(
        sender,
        text,
        type
    );


    saveMessage(
        sender,
        text,
        type
    );


    chat.scrollTop =
        chat.scrollHeight;
}


/* ==========================================================
   SEND
   ========================================================== */

async function sendMessage() {

    const message =
        messageInput.value.trim();


    if (!message) {
        return;
    }


    if (!currentChatId) {

        createChat();
    }


    const current =
        getCurrentChat();


    if (!current) {
        return;
    }


    if (
        current.messages.length === 0
    ) {

        current.title =
            generateTitle(
                message
            );

        current.updated =
            Date.now();

        currentChatTitle.textContent =
            current.title;

        saveChats();

        renderChatList();
    }


    addMessage(
        "YOU",
        message,
        "user"
    );


    messageInput.value = "";

    messageInput.style.height =
        "auto";


    sendButton.disabled =
        true;


    try {

        const response =
            await fetch(
                "/api/chat",
                {

                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            message,

                            user_name:
                                settings.name,

                            language:
                                settings.language
                        })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.error ||
                "Request failed."
            );
        }


        currentJob =
            data.job_id;


        await monitorJob();


    } catch (error) {

        addMessage(
            "DMC",
            "ERROR: " +
            error.message,
            "dmc"
        );


        sendButton.disabled =
            false;
    }
}


/* ==========================================================
   MONITOR
   ========================================================== */

async function monitorJob() {

    if (!currentJob) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/jobs/${currentJob}`
            );


        const job =
            await response.json();


        showActivity(
            job.events || []
        );


        if (
            job.status ===
            "waiting_confirmation"
        ) {

            showConfirmation(
                job.confirmation
            );

            return;
        }


        if (
            job.status ===
            "running"
        ) {

            setTimeout(
                monitorJob,
                500
            );

            return;
        }


        if (
            job.status ===
            "completed"
        ) {

            addMessage(
                "DMC",
                job.answer || "",
                "dmc"
            );


            activity.innerHTML =
                "";

            sendButton.disabled =
                false;

            currentJob =
                null;

            return;
        }


        if (
            job.status ===
            "error"
        ) {

            addMessage(
                "DMC",

                "ERROR: " +
                (
                    job.error ||
                    "Unknown error."
                ),

                "dmc"
            );


            activity.innerHTML =
                "";

            sendButton.disabled =
                false;

            currentJob =
                null;

            return;
        }


        setTimeout(
            monitorJob,
            500
        );


    } catch (error) {

        addMessage(
            "DMC",

            "Connection error: " +
            error.message,

            "dmc"
        );


        sendButton.disabled =
            false;

        currentJob =
            null;
    }
}


/* ==========================================================
   ACTIVITY
   ========================================================== */

function showActivity(events) {

    activity.innerHTML = "";

    if (!events) {
        return;
    }


    events.forEach(
        event => {

            const line =
                document.createElement(
                    "div"
                );

            line.className =
                "activity-line";

            line.textContent =
                event;

            activity.appendChild(
                line
            );
        }
    );
}


/* ==========================================================
   PIN
   ========================================================== */

function openChatMenu(
    chatId,
    event
) {

    menuChatId =
        chatId;


    const current =
        chats.find(
            chat =>
                chat.id === chatId
        );


    if (!current) {
        return;
    }


    pinChatButton.textContent =
        current.pinned
            ? "UNPIN"
            : "PIN";


    chatMenu.classList.remove(
        "hidden"
    );


    let x =
        event.clientX;

    let y =
        event.clientY;


    if (
        x + 150 >
        window.innerWidth
    ) {

        x =
            window.innerWidth -
            155;
    }


    if (
        y + 150 >
        window.innerHeight
    ) {

        y =
            window.innerHeight -
            155;
    }


    chatMenu.style.left =
        `${x}px`;

    chatMenu.style.top =
        `${y}px`;
}


function closeChatMenu() {

    chatMenu.classList.add(
        "hidden"
    );

    menuChatId =
        null;
}


pinChatButton.addEventListener(
    "click",
    () => {

        const current =
            chats.find(
                chat =>
                    chat.id ===
                    menuChatId
            );


        if (!current) {
            return;
        }


        current.pinned =
            !current.pinned;


        current.updated =
            Date.now();


        saveChats();

        renderChatList();

        closeChatMenu();
    }
);


/* ==========================================================
   RENAME
   ========================================================== */

renameChatButton.addEventListener(
    "click",
    () => {

        const current =
            chats.find(
                chat =>
                    chat.id ===
                    menuChatId
            );


        if (!current) {
            return;
        }


        const name =
            prompt(
                "Name des Chats:",
                current.title
            );


        if (
            name !== null &&
            name.trim()
        ) {

            current.title =
                name.trim();

            current.updated =
                Date.now();


            saveChats();

            renderChatList();

            renderCurrentChat();
        }


        closeChatMenu();
    }
);


/* ==========================================================
   SHARE
   ========================================================== */

shareChatButton.addEventListener(
    "click",
    async () => {

        const current =
            chats.find(
                chat =>
                    chat.id ===
                    menuChatId
            );


        if (!current) {
            return;
        }


        let text =
            `DMC CHAT: ${current.title}\n\n`;


        current.messages.forEach(
            message => {

                text +=
                    `${message.sender}: ` +
                    `${message.text}\n\n`;
            }
        );


        if (
            navigator.share
        ) {

            try {

                await navigator.share({

                    title:
                        current.title,

                    text:
                        text
                });

            } catch {
                // Share cancelled.
            }

        } else {

            try {

                await navigator.clipboard
                    .writeText(text);

                alert(
                    "Chat wurde in die Zwischenablage kopiert."
                );

            } catch {

                alert(
                    "Chat konnte nicht geteilt werden."
                );
            }
        }


        closeChatMenu();
    }
);


/* ==========================================================
   DELETE
   ========================================================== */

deleteChatButton.addEventListener(
    "click",
    () => {

        const id =
            menuChatId;


        const current =
            chats.find(
                chat =>
                    chat.id === id
            );


        if (!current) {
            return;
        }


        if (
            !confirm(
                `Chat "${current.title}" wirklich löschen?`
            )
        ) {

            closeChatMenu();

            return;
        }


        chats =
            chats.filter(
                chat =>
                    chat.id !== id
            );


        if (
            currentChatId === id
        ) {

            if (
                chats.length > 0
            ) {

                currentChatId =
                    chats[0].id;

            } else {

                currentChatId =
                    null;

                createChat();
            }
        }


        saveChats();

        renderChatList();

        renderCurrentChat();

        closeChatMenu();
    }
);


/* ==========================================================
   NEW CHAT
   ========================================================== */

newChatButton.addEventListener(
    "click",
    () => {

        createChat();
    }
);


/* ==========================================================
   SETTINGS
   ========================================================== */

settingsButton.addEventListener(
    "click",
    () => {

        applySettingsToUI();

        settingsModal.classList.remove(
            "hidden"
        );
    }
);


closeSettingsButton.addEventListener(
    "click",
    () => {

        settingsModal.classList.add(
            "hidden"
        );
    }
);


saveSettingsButton.addEventListener(
    "click",
    () => {

        settings.name =
            userNameInput.value.trim();

        settings.language =
            languageSelect.value;


        saveSettings();


        settingsModal.classList.add(
            "hidden"
        );
    }
);


/* Klick außerhalb der Settings */

settingsModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            settingsModal
        ) {

            settingsModal.classList.add(
                "hidden"
            );
        }
    }
);


/* ==========================================================
   CONFIRMATION
   ========================================================== */

function showConfirmation(data) {

    if (!data) {
        return;
    }


    confirmationTool.textContent =
        data.tool || "";


    confirmationArgs.textContent =
        JSON.stringify(
            data.args || {},
            null,
            2
        );


    confirmation.classList.remove(
        "hidden"
    );
}


allowButton.addEventListener(
    "click",
    () => {

        answerConfirmation(
            true
        );
    }
);


denyButton.addEventListener(
    "click",
    () => {

        answerConfirmation(
            false
        );
    }
);


async function answerConfirmation(
    allowed
) {

    if (!currentJob) {
        return;
    }


    confirmation.classList.add(
        "hidden"
    );


    await fetch(
        `/api/jobs/${currentJob}/confirm`,
        {

            method:
                "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body:
                JSON.stringify({
                    allowed
                })
        }
    );


    setTimeout(
        monitorJob,
        300
    );
}


/* ==========================================================
   INPUT
   ========================================================== */

sendButton.addEventListener(
    "click",
    sendMessage
);


messageInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


messageInput.addEventListener(
    "input",
    () => {

        messageInput.style.height =
            "auto";


        messageInput.style.height =
            Math.min(
                messageInput.scrollHeight,
                180
            ) + "px";
    }
);


/* ==========================================================
   CLOSE MENU
   ========================================================== */

document.addEventListener(
    "click",
    event => {

        if (
            !chatMenu.contains(
                event.target
            )
        ) {

            closeChatMenu();
        }
    }
);


/* ==========================================================
   INITIALIZE
   ========================================================== */

loadChats();

loadSettings();

applySettingsToUI();


if (
    chats.length === 0
) {

    createChat();

} else {

    currentChatId =
        chats[0].id;

    renderChatList();

    renderCurrentChat();
}


console.log(
    "DMC interface initialized."
);