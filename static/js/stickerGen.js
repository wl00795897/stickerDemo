const stickerInput = document.getElementById("sticker-input");
const ideaButton = document.getElementById("idea-btn");
const stickerContainer = document.getElementById("sticker-container");
const stickerWindow = document.getElementById("stickerWindow");
// const stickerWindowButton = document.getElementById("open-window");

let prompt = "";
let array = [];

const stickerWindowCtl = () => {
  if (stickerWindow.style.display === 'none') {
    console.log("clicked 1");
    stickerWindow.style.display = 'block'; // Show
  } else {
    console.log("clicked 2");
    stickerWindow.style.display = 'none'; // Hide
  }
};

const sendInput = async () => {
  try {
    const response = await fetch("http://localhost:5002/api/getStickers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: prompt })
    });
    const data = await response.json();
    console.log(data.images);
    array = data.images;
    stickerDisplay();
  } catch (error) {
    console.error("Error sending and fetching data to server:", error);
  }
};

const sendImage = (image) => {
    if (image == "")
      return;
    // console.log(image)
    socketio.emit("image", { data: image });
    image = "";
  };

const stickerDisplay = () => {
  stickerContainer.innerHTML = "";
  array.forEach((image, index) => {
    const imgElement = document.createElement("img");
    imgElement.src = `data:image/jpeg;base64,${image}`;
    imgElement.classList.add("stickerGenPhoto");
    imgElement.style.width = "128px";
    imgElement.style.height = "128px";
    imgElement.addEventListener("click", () => {
      sendImage(image);
    });
    stickerContainer.appendChild(imgElement);
  });
};

stickerInput.addEventListener("input", (e) => {
  prompt = e.target.value;
});

ideaButton.addEventListener("click", sendInput);

// stickerWindowButton.addEventListener("click", stickerWindowCtl);

