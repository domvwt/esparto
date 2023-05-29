// Convert document to text file.
const getDocumentFile = function () {
  let filename = document.title + ".html"
  let docString = new XMLSerializer().serializeToString(document)
  return new File([docString], filename, { type: "text/html" })
}

async function shareDocument() {
  try {
    let docFile = getDocumentFile()
    let shareData = { files: [docFile] }
    await navigator.share(shareData)
  } catch (err) {
    alert(`Error while sharing document:\n${err}`)
  }
}

const share_button = document.getElementById('share-button');

// Only show share button if web share API is supported.
if (share_button) {
  if (navigator.canShare) {
    share_button.style.display = "block";
    share_button.addEventListener('click', () => {
      shareDocument().catch(err => {
        console.error(`Error while sharing document:\n${err}`);
      });
    });
  } else {
    console.log("Web Share API not supported.")
  }
} else {
  console.log("Share button not found.")
}

const print_button = document.getElementById('print-button')

if (print_button) {
  print_button.addEventListener('click', () => {
    window.print()
  });
} else {
  console.log("Print button not found.")
}
