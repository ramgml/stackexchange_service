const changePageSize = function () {
  const pagesizeSelect = document.querySelector("select.pagesize-select");
  pagesizeSelect.addEventListener("change", (e) => {
    let params = new URLSearchParams(location.search);
    params.delete("page");
    params.set("pagesize", e.target.value);
    location.search = "?" + params.toString();
  });
};

const runWebsockeListener = function () {
  const socket = new WebSocket("ws://localhost:4000");

  socket.addEventListener("message", function (event) {
    console.log(event.data);
    message = JSON.parse(event.data)
    if ('topic' in message) {
      alert('В теме ' + topic['topic'] + ' появились изменения')
    }
  });
};

changePageSize();
runWebsockeListener();