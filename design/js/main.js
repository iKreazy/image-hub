
function triggerResizeEvent() {
  window.dispatchEvent(new Event('resize'));
}

document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggles = document.querySelectorAll('.sidebar-toggle');
  let isSidebarOpen = true;

  if (sidebar) {
    const toggleClass = (action) => {
      window.innerWidth > 578 ? document.body.classList[action]('sidebar-close') : null;
      triggerResizeEvent();
    }

    function toggleSidebar() {
      if (window.innerWidth < 578) return;
      isSidebarOpen ? toggleClass('add') : toggleClass('remove');
      isSidebarOpen = !isSidebarOpen;
    }

    sidebarToggles.forEach(toggle => {
      toggle.addEventListener('click', toggleSidebar);
    });

    sidebar.addEventListener('shown.bs.offcanvas', () => toggleClass('remove'));
    sidebar.addEventListener('hidden.bs.offcanvas', () => toggleClass('add'));

    if (window.innerWidth < 578) {
      sidebar.classList.remove('show');
      document.body.classList.add('small-device');
      document.body.classList.add('sidebar-close');
    }

    if (!sidebar.classList.contains('show')) {
      toggleClass('add');
    }
  }

  window.addEventListener('resize', () => {
    if (sidebar) {
      if (window.innerWidth > 578) {
        if (!sidebar.classList.contains('show')) {
          document.body.classList.add('sidebar-close');
        }
      }
    }

    if (window.innerWidth > 992) {
      const itemOpen = document.querySelector('.item-open');

      if (itemOpen) {
        const cardImage = itemOpen.querySelector('.card-image');
        if (cardImage) {
          const cardBody = itemOpen.querySelector('.card-body');
          const imageWidth = cardImage.getBoundingClientRect().width;
          const imageHeight = cardImage.getBoundingClientRect().height;

          const cardItem = itemOpen.querySelector('.card');
          const cardColumn = itemOpen.querySelector('.card-column-size');
          if (imageWidth >= imageHeight) {
            cardItem.classList.add('card-vertical');
            cardColumn.classList.add('col-lg-7');
            cardColumn.classList.remove('col-lg-10');
          } else {
            cardItem.classList.remove('card-vertical');
            cardColumn.classList.remove('col-lg-7');
            cardColumn.classList.add('col-lg-10');
          }

          if (cardBody) {
            cardBody.style.maxHeight = `${imageHeight}px`;

            const cardDescription = cardBody.querySelector('.card-description');
            if (cardDescription) {
              const descriptionMaxHeight = imageHeight - 50 - 64 - 30;
              cardDescription.style.maxHeight = `${descriptionMaxHeight}px`;
            }
          }
        }
      }
    } else {
      const cardBody = document.querySelector('.item-open .card-body');
      if (cardBody) {
        cardBody.style.maxHeight = '';
        const cardDescription = cardBody.querySelector('.card-description');
        if (cardDescription) {
          cardDescription.style.maxHeight = '';
        }
      }
    }
  });

  triggerResizeEvent();
  setTimeout(() => { triggerResizeEvent(); }, 200);

  Dropzone.autoDiscover = false;
  const myDropzone = new Dropzone("#my-dropzone", {
    url: '/',
    autoProcessQueue: false,
    uploadMultiple: false,
    acceptedFiles: 'image/jpeg,image/png',
    maxFiles: 1,
    previewsContainer: false,
    init: function () {
      const dropzone = this;
      const cardUpload = document.getElementById('dropzone-container');
      const hiddenFileInput = document.getElementById('hidden-file-input');
      const previewImage = document.querySelector('.upload-image');
      const removeButton = document.querySelector('.upload-remove');
      const uploadDrop = document.querySelector('.upload-drop');
      const defaultContent = cardUpload.innerHTML;

      dropzone.on('addedfile', function (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          previewImage.src = e.target.result;
          cardUpload.classList.add('selected');

          const dataTransfer = new DataTransfer();
          dataTransfer.items.add(file);
          hiddenFileInput.files = dataTransfer.files;
        };
        reader.readAsDataURL(file);
      });

      removeButton.addEventListener('click', function () {
        dropzone.removeAllFiles(true);
        hiddenFileInput.value = '';
        cardUpload.classList.remove('selected');
      });

      dropzone.on("addedfile", function(file) {
        if (dropzone.files.length > 1) {
          dropzone.removeFile(dropzone.files[0]);
        }
      });
    }
  });
});