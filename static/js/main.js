/**
 * College Lost Things and Found System - Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initImageUploadPreview();
  initFormValidations();
  initFoundItemsFilter();
  initModals();
});

/* Mobile Navbar Toggle */
function initMobileNav() {
  const toggleBtn = document.getElementById('mobileNavToggle');
  const navLinks = document.getElementById('navLinks');

  if (toggleBtn && navLinks) {
    toggleBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isOpen = navLinks.classList.contains('active');
      toggleBtn.innerHTML = isOpen ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    });
  }
}

/* Image Upload Preview & Validation */
function initImageUploadPreview() {
  const dropzone = document.getElementById('imageDropzone');
  const fileInput = document.getElementById('imageUploadInput');
  const previewWrapper = document.getElementById('imagePreviewWrapper');
  const previewImg = document.getElementById('imagePreviewImg');
  const previewName = document.getElementById('imagePreviewName');

  if (!fileInput) return;

  function handleFileSelect(file) {
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg', 'image/svg+xml'];
    if (!validTypes.includes(file.type)) {
      showToast('Please upload a valid image file (JPG, PNG, WEBP, SVG)', 'error');
      fileInput.value = '';
      if (previewWrapper) previewWrapper.style.display = 'none';
      return;
    }

    // Validate size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      showToast('Image size exceeds 5MB limit', 'error');
      fileInput.value = '';
      if (previewWrapper) previewWrapper.style.display = 'none';
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (previewImg) previewImg.src = e.target.result;
      if (previewName) previewName.textContent = file.name;
      if (previewWrapper) previewWrapper.style.display = 'flex';
    };
    reader.readAsDataURL(file);
  }

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });

  if (dropzone) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect(files[0]);
      }
    });
  }
}

/* Client-Side Form Validations */
function initFormValidations() {
  const forms = document.querySelectorAll('form[data-validate="true"]');

  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      let isValid = true;
      const mobileInput = form.querySelector('input[name="mobile"]');

      if (mobileInput) {
        const phoneRegex = /^[0-9]{10}$/;
        const val = mobileInput.value.trim();
        if (!phoneRegex.test(val)) {
          showToast('Please enter a valid 10-digit mobile number', 'error');
          mobileInput.focus();
          isValid = false;
          e.preventDefault();
          return;
        }
      }

      // Check required fields
      const requiredInputs = form.querySelectorAll('[required]');
      requiredInputs.forEach(input => {
        if (!input.value.trim()) {
          input.classList.add('is-invalid');
          isValid = false;
        } else {
          input.classList.remove('is-invalid');
        }
      });

      if (!isValid) {
        e.preventDefault();
        showToast('Please fill out all required fields correctly', 'error');
      }
    });
  });
}

/* Client-Side Search & Filter for Found Items */
function initFoundItemsFilter() {
  const searchInput = document.getElementById('foundSearchInput');
  const chipContainer = document.getElementById('categoryChips');
  const itemsContainer = document.getElementById('foundItemsGrid');

  if (!itemsContainer) return;

  const itemCards = itemsContainer.querySelectorAll('.item-card');

  function filterCards() {
    const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const activeChip = chipContainer ? chipContainer.querySelector('.chip.active') : null;
    const selectedCategory = activeChip ? activeChip.getAttribute('data-category') : 'All';

    let visibleCount = 0;

    itemCards.forEach(card => {
      const title = card.getAttribute('data-title') || '';
      const category = card.getAttribute('data-category') || '';
      const desc = card.getAttribute('data-desc') || '';
      const location = card.getAttribute('data-place') || '';

      const matchesCategory = (selectedCategory === 'All' || category === selectedCategory);
      const matchesSearch = !searchTerm || 
        title.toLowerCase().includes(searchTerm) || 
        desc.toLowerCase().includes(searchTerm) || 
        location.toLowerCase().includes(searchTerm);

      if (matchesCategory && matchesSearch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    const noResultsMsg = document.getElementById('noResultsMessage');
    if (noResultsMsg) {
      noResultsMsg.style.display = (visibleCount === 0) ? 'block' : 'none';
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterCards);
  }

  if (chipContainer) {
    const chips = chipContainer.querySelectorAll('.chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        filterCards();
      });
    });
  }
}

/* Modal Window Management */
function initModals() {
  const modalTriggers = document.querySelectorAll('[data-modal-target]');
  const modalCloses = document.querySelectorAll('[data-modal-close]');

  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = trigger.getAttribute('data-modal-target');
      const modal = document.getElementById(targetId);
      if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  modalCloses.forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
      const modal = closeBtn.closest('.modal-overlay');
      if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });

  // Close modal when clicking backdrop
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });
}

/* Toast Notifications */
function showToast(message, type = 'info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const iconMap = {
    success: '<i class="fas fa-check-circle" style="color:#10b981;"></i>',
    error: '<i class="fas fa-exclamation-circle" style="color:#ef4444;"></i>',
    info: '<i class="fas fa-info-circle" style="color:#3b82f6;"></i>'
  };

  toast.innerHTML = `${iconMap[type] || ''} <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
