// Image preview function
function showImagePreview(imageUrl, galleryGrid) {
    const imageModal = document.getElementById('image-modal');
    const modalImage = imageModal.querySelector('.modal-image');
    const prevButton = imageModal.querySelector('.prev-image');
    const nextButton = imageModal.querySelector('.next-image');
    const closeButton = imageModal.querySelector('.close-modal');
    
    // Get all images in the current gallery
    const allImages = Array.from(galleryGrid.querySelectorAll('.gallery-item img'));
    const currentIndex = allImages.findIndex(img => img.src === imageUrl);
    
    // Show/hide navigation buttons based on position
    prevButton.style.display = currentIndex > 0 ? 'flex' : 'none';
    nextButton.style.display = currentIndex < allImages.length - 1 ? 'flex' : 'none';
    
    // Update image source
    modalImage.src = imageUrl;
    imageModal.classList.add('active');
    
    // Navigation function
    function navigateImage(direction) {
        const newIndex = currentIndex + direction;
        if (newIndex >= 0 && newIndex < allImages.length) {
            const newImage = allImages[newIndex];
            showImagePreview(newImage.src, galleryGrid);
        }
    }
    
    // Event listeners for navigation
    prevButton.onclick = () => navigateImage(-1);
    nextButton.onclick = () => navigateImage(1);
    
    // Close modal handler
    function closeModal() {
        imageModal.classList.remove('active');
        document.removeEventListener('keydown', handleKeyPress);
    }
    
    // Close button and click outside
    closeButton.onclick = closeModal;
    imageModal.onclick = (e) => {
        if (e.target === imageModal) {
            closeModal();
        }
    };
    
    // Keyboard navigation
    function handleKeyPress(e) {
        if (e.key === 'ArrowLeft' && currentIndex > 0) {
            navigateImage(-1);
        } else if (e.key === 'ArrowRight' && currentIndex < allImages.length - 1) {
            navigateImage(1);
        } else if (e.key === 'Escape') {
            closeModal();
        }
    }
    
    document.addEventListener('keydown', handleKeyPress);
}

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference
    if (localStorage.getItem('darkMode') === 'true') {
        body.classList.add('dark-mode');
        themeToggle.querySelector('.material-icons').textContent = 'light_mode';
    }

    themeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        const isDarkMode = body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        themeToggle.querySelector('.material-icons').textContent = isDarkMode ? 'light_mode' : 'dark_mode';
    });

    // View toggle (list/grid)
    const viewToggle = document.getElementById('view-toggle');
    const cardsContainer = document.querySelector('.cards-container');
    
    // Check for saved view preference
    if (localStorage.getItem('viewMode') === 'grid') {
        cardsContainer.classList.remove('list');
        cardsContainer.classList.add('grid');
        viewToggle.querySelector('.material-icons').textContent = 'view_list';
    }

    viewToggle.addEventListener('click', () => {
        cardsContainer.classList.toggle('list');
        cardsContainer.classList.toggle('grid');
        const isGridView = cardsContainer.classList.contains('grid');
        localStorage.setItem('viewMode', isGridView ? 'grid' : 'list');
        viewToggle.querySelector('.material-icons').textContent = isGridView ? 'view_list' : 'grid_view';
    });

    // Profile menu
    const profileButton = document.querySelector('.profile-button');
    const profileMenu = document.querySelector('.profile-menu-content');
    
    profileButton.addEventListener('click', function(e) {
        e.stopPropagation();
        profileMenu.classList.toggle('active');
    });

    document.addEventListener('click', function(e) {
        if (!profileMenu.contains(e.target) && !profileButton.contains(e.target)) {
            profileMenu.classList.remove('active');
        }
    });

    // New Card functionality
    const newCardButton = document.getElementById('new-card-button');
    const newCardModal = document.getElementById('new-card-modal');
    const newCardForm = document.getElementById('new-card-form');
    
    newCardButton.addEventListener('click', function() {
        newCardModal.classList.add('active');
    });

    newCardForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const title = document.getElementById('card-title').value;
        const description = document.getElementById('card-description').value;

        fetch('/api/cards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description
            })
        })
        .then(response => response.json())
        .then(card => {
            // Create new card element
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.dataset.cardId = card.id;
            cardElement.innerHTML = `
                <div class="card-header">
                    <h2 class="card-title">${card.title}</h2>
                    <div class="card-actions">
                        <button class="card-action-button edit-card" title="Edit">
                            <span class="material-icons">edit</span>
                        </button>
                        <button class="card-action-button share-card" title="Share">
                            <span class="material-icons">share</span>
                        </button>
                        <button class="card-action-button delete-card" title="Delete">
                            <span class="material-icons">delete</span>
                        </button>
                    </div>
                </div>
                <div class="card-content">
                    <p class="card-description">${card.description}</p>
                </div>
                <div class="card-gallery">
                    <div class="gallery-header">
                        <h3 class="gallery-title">Gallery</h3>
                    </div>
                    <div class="gallery-grid"></div>
                    <div class="upload-area" data-type="image">
                        <span class="material-icons">cloud_upload</span>
                        <p>Click or drag images here to upload</p>
                        <input type="file" class="file-input" multiple accept="image/*" style="display: none;">
                    </div>
                </div>
                <div class="card-files">
                    <div class="files-header">
                        <h3 class="files-title">Files</h3>
                    </div>
                    <div class="files-list"></div>
                    <div class="upload-area" data-type="file">
                        <span class="material-icons">cloud_upload</span>
                        <p>Click or drag files here to upload</p>
                        <input type="file" class="file-input" multiple style="display: none;">
                    </div>
                </div>
            `;

            // Add to container
            cardsContainer.insertBefore(cardElement, cardsContainer.firstChild);

            // Close modal and reset form
            newCardModal.classList.remove('active');
            newCardForm.reset();
        })
        .catch(error => {
            console.error('Error creating card:', error);
            alert('Failed to create card. Please try again.');
        });
    });

    // Close modals when clicking cancel
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.modal').classList.remove('active');
        });
    });

    // Close modals when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });

    // Custom confirm dialog
    function showConfirmDialog(title, message) {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirm-modal');
            const titleEl = modal.querySelector('.modal-title');
            const messageEl = modal.querySelector('.modal-message');
            const confirmBtn = modal.querySelector('.confirm-button');
            const cancelBtn = modal.querySelector('.cancel-button');

            titleEl.textContent = title;
            messageEl.textContent = message;
            modal.classList.add('active');

            const handleConfirm = () => {
                modal.classList.remove('active');
                cleanup();
                resolve(true);
            };

            const handleCancel = () => {
                modal.classList.remove('active');
                cleanup();
                resolve(false);
            };

            const handleOutsideClick = (e) => {
                if (e.target === modal) {
                    handleCancel();
                }
            };

            const cleanup = () => {
                confirmBtn.removeEventListener('click', handleConfirm);
                cancelBtn.removeEventListener('click', handleCancel);
                modal.removeEventListener('click', handleOutsideClick);
            };

            confirmBtn.addEventListener('click', handleConfirm);
            cancelBtn.addEventListener('click', handleCancel);
            modal.addEventListener('click', handleOutsideClick);
        });
    }

    // Card management
    document.addEventListener('click', async (e) => {
        const deleteBtn = e.target.closest('.delete-card');
        const editBtn = e.target.closest('.edit-card');
        const shareBtn = e.target.closest('.share-card');
        const removeFileBtn = e.target.closest('.remove-file');
        const downloadBtn = e.target.closest('.download-file, .download-btn');
        const imageItem = e.target.closest('.image-item img');

        if (editBtn) {
            const card = editBtn.closest('.card');
            toggleEditMode(card);
        } else if (shareBtn) {
            const card = shareBtn.closest('.card');
            showShareModal(card.dataset.cardId);
        } else if (deleteBtn) {
            const card = deleteBtn.closest('.card');
            const confirmed = await showConfirmDialog(
                'Delete Card',
                'Are you sure you want to delete this card? This action cannot be undone.'
            );
            if (confirmed) {
                try {
                    const cardId = card.dataset.cardId;
                    const response = await fetch(`/api/cards/${cardId}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'Failed to delete card');
                    }
                    
                    const data = await response.json();
                    if (data.message === "Card deleted successfully") {
                        card.remove();
                    } else {
                        throw new Error('Unexpected response from server');
                    }
                } catch (error) {
                    console.error('Error deleting card:', error);
                    alert(`Failed to delete card: ${error.message}`);
                }
            }
        } else if (removeFileBtn) {
            const fileItem = removeFileBtn.closest('.file-item, .image-item');
            const card = fileItem.closest('.card');
            const fileId = fileItem.dataset.fileId;
            const cardId = card.dataset.cardId;

            const confirmed = await showConfirmDialog(
                'Delete File',
                'Are you sure you want to delete this file? This action cannot be undone.'
            );
            
            if (confirmed) {
                try {
                    const response = await fetch(`/api/cards/${cardId}/files/${fileId}`, {
                        method: 'DELETE'
                    });
                    
                    if (!response.ok) throw new Error('Failed to delete file');
                    fileItem.remove();
                } catch (error) {
                    console.error('Error deleting file:', error);
                    alert('Failed to delete file. Please try again.');
                }
            }
        } else if (downloadBtn) {
            const fileItem = downloadBtn.closest('.file-item, .gallery-item');
            if (!fileItem) return;
            let url;
            if (fileItem.classList.contains('gallery-item')) {
                url = fileItem.querySelector('img').dataset.url || fileItem.querySelector('img').src;
            } else {
                url = fileItem.dataset.url;
            }
            if (url) {
                // Extract filename from URL
                const filename = url.split('/').pop();
                // Create an anchor element, set download attribute and trigger click
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        } else if (imageItem) {
            showImagePreview(imageItem.src, imageItem.closest('.gallery-grid'));
        }
    });

    function toggleEditMode(card) {
        const isEditing = card.classList.toggle('editing');
        const title = card.querySelector('.card-title');
        const description = card.querySelector('.card-description');
        const editButton = card.querySelector('.edit-card');
        const editIcon = editButton.querySelector('.material-icons');
        
        if (isEditing) {
            // Store original values
            card.dataset.originalTitle = title.textContent;
            card.dataset.originalDescription = description.textContent;
            
            // Make elements editable
            title.contentEditable = true;
            description.contentEditable = true;
            title.focus();
            
            // Change edit button icon
            editIcon.textContent = 'save';
            
            // Show delete buttons
            card.querySelectorAll('.delete-file.edit-only').forEach(button => {
                button.style.display = 'inline-flex';
            });
        } else {
            // Save changes
            saveCardChanges(card);
            
            // Reset edit button icon
            editIcon.textContent = 'edit';
            
            // Make elements non-editable
            title.contentEditable = false;
            description.contentEditable = false;
            
            // Hide delete buttons
            card.querySelectorAll('.delete-file.edit-only').forEach(button => {
                button.style.display = 'none';
            });
        }
    }

    function saveCardChanges(card) {
        const cardId = card.dataset.cardId;
        const title = card.querySelector('.card-title').textContent.trim();
        const description = card.querySelector('.card-description').textContent.trim();

        fetch(`/api/cards/${cardId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description
            })
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to update card');
            return response.json();
        })
        .then(data => {
            console.log('Card updated successfully:', data);
        })
        .catch(error => {
            console.error('Error updating card:', error);
            alert('Failed to save changes. Please try again.');
        });
    }

    function exitEditMode(card) {
        card.classList.remove('editing');
        const editButton = card.querySelector('.edit-card');
        editButton.classList.remove('active');

        const title = card.querySelector('.card-title');
        const description = card.querySelector('.card-description');

        title.contentEditable = 'false';
        description.contentEditable = 'false';
        title.classList.remove('editing');
        description.classList.remove('editing');
    }

    // File upload handling
    document.addEventListener('click', (e) => {
        const uploadArea = e.target.closest('.upload-area');
        if (uploadArea) {
            const fileInput = uploadArea.querySelector('.file-input');
            fileInput.click();
        }
    });

    document.addEventListener('change', async (e) => {
        const fileInput = e.target.closest('.file-input');
        if (fileInput) {
            const uploadArea = fileInput.closest('.upload-area');
            const card = uploadArea.closest('.card');
            const cardId = card.dataset.cardId;
            const type = uploadArea.dataset.type;
            
            const formData = new FormData();
            formData.append('type', type);
            
            Array.from(fileInput.files).forEach(file => {
                formData.append('files[]', file);
            });

            try {
                console.log('Uploading files...', formData);
                const response = await fetch(`/api/cards/${cardId}/files`, {
                    method: 'POST',
                    body: formData
                });

                console.log('Upload response status:', response.status);
                const data = await response.json();
                console.log('Upload response data:', data);

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to upload files');
                }

                data.files.forEach(file => {
                    if (file.is_image) {
                        const galleryGrid = card.querySelector('.gallery-grid');
                        const imageElement = document.createElement('div');
                        imageElement.className = 'gallery-item';
                        imageElement.dataset.fileId = file.id;
                        imageElement.innerHTML = `
                            <img src="${file.url}" alt="${file.name}" class="preview-image" data-url="${file.url}">
                            <div class="file-actions">
                                <button class="download-file" title="Download file">
                                    <span class="material-icons">download</span>
                                </button>
                                <button class="delete-file edit-only" title="Delete file">
                                    <span class="material-icons">delete</span>
                                </button>
                            </div>
                        `;
                        galleryGrid.appendChild(imageElement);
                        
                        // Add click handler for image preview
                        const img = imageElement.querySelector('.preview-image');
                        img.addEventListener('click', function() {
                            showImagePreview(this.dataset.url, this.closest('.gallery-grid'));
                        });
                    } else {
                        const filesList = card.querySelector('.files-list');
                        const fileElement = document.createElement('div');
                        fileElement.className = 'file-item';
                        fileElement.dataset.fileId = file.id;
                        fileElement.dataset.url = file.url;
                        fileElement.innerHTML = `
                            <span class="file-name">${file.name}</span>
                            <div class="file-actions">
                                <button class="download-file" title="Download file">
                                    <span class="material-icons">download</span>
                                </button>
                                <button class="delete-file edit-only" title="Delete file">
                                    <span class="material-icons">delete</span>
                                </button>
                            </div>
                        `;
                        filesList.appendChild(fileElement);
                    }
                });

                // Clear the input
                fileInput.value = '';
            } catch (error) {
                console.error('Error uploading files:', error);
                alert('Failed to upload files. Please try again.');
            }
        }
    });

    // Drag and drop handling
    document.addEventListener('dragover', (e) => {
        const uploadArea = e.target.closest('.upload-area');
        if (uploadArea) {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        }
    });

    document.addEventListener('dragleave', (e) => {
        const uploadArea = e.target.closest('.upload-area');
        if (uploadArea) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        }
    });

    document.addEventListener('drop', async (e) => {
        const uploadArea = e.target.closest('.upload-area');
        if (uploadArea) {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            
            const card = uploadArea.closest('.card');
            const cardId = card.dataset.cardId;
            const type = uploadArea.dataset.type;
            const files = e.dataTransfer.files;
            
            const formData = new FormData();
            formData.append('type', type);
            
            Array.from(files).forEach(file => {
                if (type === 'image' && file.type.startsWith('image/')) {
                    formData.append('files[]', file);
                } else if (type === 'file' && !file.type.startsWith('image/')) {
                    formData.append('files[]', file);
                }
            });

            try {
                console.log('Uploading files...', formData);
                const response = await fetch(`/api/cards/${cardId}/files`, {
                    method: 'POST',
                    body: formData
                });

                console.log('Upload response status:', response.status);
                const data = await response.json();
                console.log('Upload response data:', data);

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to upload files');
                }

                data.files.forEach(file => {
                    if (file.is_image) {
                        const galleryGrid = card.querySelector('.gallery-grid');
                        const imageElement = document.createElement('div');
                        imageElement.className = 'gallery-item';
                        imageElement.dataset.fileId = file.id;
                        imageElement.innerHTML = `
                            <img src="${file.url}" alt="${file.name}" class="preview-image" data-url="${file.url}">
                            <div class="file-actions">
                                <button class="download-file" title="Download file">
                                    <span class="material-icons">download</span>
                                </button>
                                <button class="delete-file edit-only" title="Delete file">
                                    <span class="material-icons">delete</span>
                                </button>
                            </div>
                        `;
                        galleryGrid.appendChild(imageElement);
                        
                        // Add click handler for image preview
                        const img = imageElement.querySelector('.preview-image');
                        img.addEventListener('click', function() {
                            showImagePreview(this.dataset.url, this.closest('.gallery-grid'));
                        });
                    } else {
                        const filesList = card.querySelector('.files-list');
                        const fileElement = document.createElement('div');
                        fileElement.className = 'file-item';
                        fileElement.dataset.fileId = file.id;
                        fileElement.dataset.url = file.url;
                        fileElement.innerHTML = `
                            <span class="file-name">${file.name}</span>
                            <div class="file-actions">
                                <button class="download-file" title="Download file">
                                    <span class="material-icons">download</span>
                                </button>
                                <button class="delete-file edit-only" title="Delete file">
                                    <span class="material-icons">delete</span>
                                </button>
                            </div>
                        `;
                        filesList.appendChild(fileElement);
                    }
                });
            } catch (error) {
                console.error('Error uploading files:', error);
                alert('Failed to upload files. Please try again.');
            }
        }
    });

    // Search functionality
    const searchInput = document.querySelector('.search-container input');
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        document.querySelectorAll('.card').forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const description = card.querySelector('.card-description').textContent.toLowerCase();
            const isVisible = title.includes(searchTerm) || description.includes(searchTerm);
            card.style.display = isVisible ? '' : 'none';
        });
    });

    // Share card functionality
    function showShareModal(cardId) {
        const modal = document.getElementById('share-modal');
        const form = document.getElementById('share-form');
        
        modal.classList.add('active');
        form.dataset.cardId = cardId;

        // Remove any existing submit handler
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);

        // Close modal when clicking outside
        const handleOutsideClick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
                modal.removeEventListener('click', handleOutsideClick);
            }
        };
        modal.addEventListener('click', handleOutsideClick);

        // Close modal when clicking cancel
        newForm.querySelector('.cancel-button').addEventListener('click', () => {
            modal.classList.remove('active');
            modal.removeEventListener('click', handleOutsideClick);
        });

        newForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[name="email"]').value;
            const permission = this.querySelector('input[name="permission"]:checked').value;
            
            fetch(`/api/cards/${cardId}/share`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    email: email,
                    permission: permission
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Failed to share card');
                return response.json();
            })
            .then(data => {
                modal.classList.remove('active');
                this.reset();
                alert('Card shared successfully!');
            })
            .catch(error => {
                console.error('Error sharing card:', error);
                alert('Failed to share card. Please try again.');
            });
        });
    }

    document.addEventListener('click', async (e) => {
        const deleteButton = e.target.closest('.delete-file');
        if (deleteButton) {
            e.preventDefault();
            const fileItem = deleteButton.closest('.gallery-item, .file-item');
            const card = deleteButton.closest('.card');
            const cardId = card.dataset.cardId;
            const fileId = fileItem.dataset.fileId;

            if (await showConfirmDialog('Delete File', 'Are you sure you want to delete this file?')) {
                try {
                    const response = await fetch(`/api/cards/${cardId}/files/${fileId}`, {
                        method: 'DELETE'
                    });

                    if (!response.ok) {
                        throw new Error('Failed to delete file');
                    }

                    fileItem.remove();
                } catch (error) {
                    console.error('Error deleting file:', error);
                    alert('Failed to delete file. Please try again.');
                }
            }
        }
    });
//den stuff evtl entfernen wenn er nicht geht.
    document.addEventListener('click', async (e) => {
        // ...existing code for buttons...
        const imagePreview = e.target.closest('.preview-image');
        if (imagePreview) {
            // Use the data-url attribute and nearest gallery grid container for preview
            showImagePreview(imagePreview.dataset.url, imagePreview.closest('.gallery-grid'));
        }
        // ...existing code...
    });
});
