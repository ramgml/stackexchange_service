const pagesizeSelect = document.querySelector("select.pagesize-select");
pagesizeSelect.addEventListener("change", (e) => {
  let params = new URLSearchParams(location.search);
  params.delete('page')
  params.set('pagesize', e.target.value)
  location.search = '?' + params.toString()
});
