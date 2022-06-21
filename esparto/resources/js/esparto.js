// Convert document to text file.
const getDocumentFile = function () {
  let filename = document.title + ".html"
  let docString = new XMLSerializer().serializeToString(document)
  return new File([docString], filename, { type: "text/html" })
}

const share_button = document.getElementById('share-button');

// Only show share button if web share API is supported.
if (navigator.canShare) {
  share_button.style.display = "block";
} else {
  console.log("Web Share API not supported.")
}

// Share must be triggered by "user activation".
share_button.addEventListener('click', async () => {
  try {
    let docFile = getDocumentFile()
    let shareData = { files: [docFile] }
    await navigator.share(shareData)
  } catch (err) {
    alert(`Error while sharing document:\n${err}`)
  }
});


const print_button = document.getElementById('print-button')

print_button.addEventListener('click', () => {
  window.print()
});
