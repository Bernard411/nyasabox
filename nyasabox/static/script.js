class MusicPlayer {
    constructor() {
        this.audio = document.getElementById('audioPlayer');
        this.songs = JSON.parse('{{ songs_json|safe }}');
        this.currentIndex = -1;
        this.isPlaying = false;
        this.isShuffled = false;
        this.isRepeating = false;
        this.volume = 0.7;
        this.currentSlide = 0;
        this.slideInterval = null;

        this.initializePlayer();
        this.setupEventListeners();
        this.startCarousel();
    }

    initializePlayer() {
        this.audio.volume = this.volume;
        this.updateVolumeDisplay();
        this.setTheme();
    }

    setupEventListeners() {
        // Menu toggle for mobile
        document.getElementById('menuToggle').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });

        // Player controls
        document.getElementById('playPauseBtn').addEventListener('click', () => {
            this.togglePlayPause();
        });

        document.getElementById('nextBtn').addEventListener('click', () => {
            this.nextSong();
        });

        document.getElementById('prevBtn').addEventListener('click', () => {
            this.previousSong();
        });

        document.getElementById('shuffleBtn').addEventListener('click', () => {
            this.toggleShuffle();
        });

        document.getElementById('repeatBtn').addEventListener('click', () => {
            this.toggleRepeat();
        });

        // Progress bar
        document.getElementById('progressBar').addEventListener('click', (e) => {
            this.seekTo(e);
        });

        // Volume control
        document.getElementById('volumeBar').addEventListener('click', (e) => {
            this.setVolume(e);
        });

        document.getElementById('volumeBtn').addEventListener('click', () => {
            this.toggleMute();
        });

        // Audio events
        this.audio.addEventListener('timeupdate', () => {
            this.updateProgress();
        });

        this.audio.addEventListener('ended', () => {
            this.handleSongEnd();
        });

        this.audio.addEventListener('loadedmetadata', () => {
            this.updateTotalTime();
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchSongs(e.target.value);
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Carousel controls
        document.querySelectorAll('.dot').forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.goToSlide(index);
            });
        });

        // Song selection
        document.querySelectorAll('.music-card, .track-item').forEach((item) => {
            item.addEventListener('click', (e) => {
                const index = parseInt(item.dataset.index);
                if (e.target.classList.contains('download-btn')) return;
                this.playSong(index);
            });
        });

        // Play buttons
        document.querySelectorAll('.play-btn').forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const index = parseInt(btn.dataset.index);
                this.playSong(index);
            });
        });

        // Upload functionality
        document.getElementById('fileInput')?.addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });

        // Fullscreen button
        document.getElementById('fullscreenBtn')?.addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Playlist item clicks (placeholder)
        document.querySelectorAll('.playlist-item').forEach((item) => {
            item.addEventListener('click', () => {
                this.showNotification('Playlist functionality not implemented', 'info');
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    startCarousel() {
        this.slideInterval = setInterval(() => {
            this.nextSlide();
        }, 5000);
    }

    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % 3;
        this.updateCarousel();
    }

    goToSlide(index) {
        this.currentSlide = index;
        this.updateCarousel();
        clearInterval(this.slideInterval);
        this.startCarousel();
    }

    updateCarousel() {
        const slides = document.querySelectorAll('.hero-slide');
        const dots = document.querySelectorAll('.dot');

        slides.forEach((slide, index) => {
            slide.classList.toggle('active', index === this.currentSlide);
        });

        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentSlide);
        });
    }

    playSong(index) {
        if (!this.songs[index]) return;

        this.currentIndex = index;
        const song = this.songs[index];

        this.audio.src = song.url;
        this.audio.play().then(() => {
            this.isPlaying = true;
            this.updatePlayerDisplay();
            this.updatePlayPauseButton();
            document.body.classList.add('playing');
        }).catch((error) => {
            this.showNotification('Error playing song', 'error');
            console.error('Playback error:', error);
        });
    }

    togglePlayPause() {
        if (this.currentIndex === -1) {
            if (this.songs.length > 0) {
                this.playSong(0);
            } else {
                this.showNotification('No songs available', 'info');
            }
            return;
        }

        if (this.isPlaying) {
            this.audio.pause();
            this.isPlaying = false;
            document.body.classList.remove('playing');
        } else {
            this.audio.play().then(() => {
                this.isPlaying = true;
                document.body.classList.add('playing');
            }).catch((error) => {
                this.showNotification('Error playing song', 'error');
            });
        }
        this.updatePlayPauseButton();
    }

    nextSong() {
        if (this.songs.length === 0) return;

        if (this.isShuffled) {
            this.currentIndex = Math.floor(Math.random() * this.songs.length);
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.songs.length;
        }

        this.playSong(this.currentIndex);
    }

    previousSong() {
        if (this.songs.length === 0) return;

        this.currentIndex = this.currentIndex > 0 ? this.currentIndex - 1 : this.songs.length - 1;
        this.playSong(this.currentIndex);
    }

    toggleShuffle() {
        this.isShuffled = !this.isShuffled;
        const shuffleBtn = document.getElementById('shuffleBtn');
        shuffleBtn.style.color = this.isShuffled ? 'var(--accent-primary)' : 'var(--text-primary)';
        this.showNotification(this.isShuffled ? 'Shuffle on' : 'Shuffle off');
    }

    toggleRepeat() {
        this.isRepeating = !this.isRepeating;
        const repeatBtn = document.getElementById('repeatBtn');
        repeatBtn.style.color = this.isRepeating ? 'var(--accent-primary)' : 'var(--text-primary)';
        this.showNotification(this.isRepeating ? 'Repeat on' : 'Repeat off');
    }

    handleSongEnd() {
        if (this.isRepeating) {
            this.audio.currentTime = 0;
            this.audio.play();
        } else {
            this.nextSong();
        }
    }

    seekTo(e) {
        if (!this.audio.duration) return;

        const progressBar = document.getElementById('progressBar');
        const rect = progressBar.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;
        const duration = this.audio.duration;

        this.audio.currentTime = (clickX / width) * duration;
    }

    setVolume(e) {
        const volumeBar = document.getElementById('volumeBar');
        const rect = volumeBar.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const width = rect.width;

        this.volume = Math.max(0, Math.min(1, clickX / width));
        this.audio.volume = this.volume;
        this.updateVolumeDisplay();
        this.updateVolumeIcon();
    }

    toggleMute() {
        if (this.audio.volume > 0) {
            this.audio.volume = 0;
        } else {
            this.audio.volume = this.volume;
        }
        this.updateVolumeDisplay();
        this.updateVolumeIcon();
    }

    updateVolumeIcon() {
        const volumeBtn = document.getElementById('volumeBtn');
        const icon = volumeBtn.querySelector('.material-icons');

        if (this.audio.volume === 0) {
            icon.textContent = 'volume_off';
        } else if (this.audio.volume < 0.5) {
            icon.textContent = 'volume_down';
        } else {
            icon.textContent = 'volume_up';
        }
    }

    updateProgress() {
        if (!this.audio.duration) return;

        const progress = (this.audio.currentTime / this.audio.duration) * 100;
        document.getElementById('progress').style.width = `${progress}%`;
        document.getElementById('currentTime').textContent = this.formatTime(this.audio.currentTime);
    }

    updateTotalTime() {
        document.getElementById('totalTime').textContent = this.formatTime(this.audio.duration);
    }

    updateVolumeDisplay() {
        const volumeProgress = document.getElementById('volumeProgress');
        volumeProgress.style.width = `${this.audio.volume * 100}%`;
    }

    updatePlayerDisplay() {
        const song = this.songs[this.currentIndex];
        if (!song) return;

        document.getElementById('currentTitle').textContent = song.title;
        document.getElementById('currentArtist').textContent = song.artist;
        const cover = document.getElementById('currentCover');
        cover.innerHTML = song.cover_image ? `<img src="${song.cover_image}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 0.75rem;">` : '<span class="material-icons">music_note</span>';
    }

    updatePlayPauseButton() {
        const btn = document.getElementById('playPauseBtn');
        const icon = btn.querySelector('.material-icons');
        icon.textContent = this.isPlaying ? 'pause' : 'play_arrow';
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';

        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    searchSongs(query) {
        const trackItems = document.querySelectorAll('.track-item');
        const musicCards = document.querySelectorAll('.music-card');

        const searchTerm = query.toLowerCase();

        trackItems.forEach((item, index) => {
            const song = this.songs[index];
            const matches = song.title.toLowerCase().includes(searchTerm) ||
                           song.artist.toLowerCase().includes(searchTerm);

            item.style.display = matches ? 'grid' : 'none';
        });

        musicCards.forEach((card, index) => {
            const song = this.songs[index];
            const matches = song.title.toLowerCase().includes(searchTerm) ||
                           song.artist.toLowerCase().includes(searchTerm);

            card.style.display = matches ? 'block' : 'none';
        });
    }

    toggleTheme() {
        const isLightMode = document.body.classList.toggle('light-mode');
        const themeIcon = document.getElementById('themeToggle').querySelector('.material-icons');
        themeIcon.textContent = isLightMode ? 'light_mode' : 'dark_mode';

        localStorage.setItem('theme', isLightMode ? 'light' : 'dark');
        this.showNotification(`Switched to ${isLightMode ? 'light' : 'dark'} mode`);
    }

    setTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-mode');
            document.getElementById('themeToggle').querySelector('.material-icons').textContent = 'light_mode';
        }
    }

    handleFileUpload(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.showNotification(`Selected ${files.length} file(s) for upload`, 'info');
            // Note: Actual file upload requires server-side handling (e.g., via AJAX to Django endpoint)
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().then(() => {
                this.showNotification('Entered fullscreen mode');
            }).catch((err) => {
                this.showNotification('Failed to enter fullscreen mode', 'error');
            });
        } else {
            document.exitFullscreen().then(() => {
                this.showNotification('Exited fullscreen mode');
            }).catch((err) => {
                this.showNotification('Failed to exit fullscreen mode', 'error');
            });
        }
    }

    handleKeyboardShortcuts(e) {
        if (e.target.tagName === 'INPUT') return;

        switch(e.code) {
            case 'Space':
                e.preventDefault();
                this.togglePlayPause();
                break;
            case 'ArrowRight':
                if (e.shiftKey) {
                    e.preventDefault();
                    this.nextSong();
                }
                break;
            case 'ArrowLeft':
                if (e.shiftKey) {
                    e.preventDefault();
                    this.previousSong();
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.audio.volume = Math.min(1, this.audio.volume + 0.1);
                this.volume = this.audio.volume;
                this.updateVolumeDisplay();
                this.updateVolumeIcon();
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.audio.volume = Math.max(0, this.audio.volume - 0.1);
                this.volume = this.audio.volume;
                this.updateVolumeDisplay();
                this.updateVolumeIcon();
                break;
            case 'KeyF':
                e.preventDefault();
                this.toggleFullscreen();
                break;
        }
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="material-icons">${type === 'error' ? 'error' : type === 'info' ? 'info' : 'check_circle'}</span>
            <span>${message}</span>
        `;

        Object.assign(notification.style, {
            position: 'fixed',
            top: '2rem',
            right: '2rem',
            background: type === 'error' ? '#ff4757' : type === 'info' ? '#3742fa' : '#2ed573',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            zIndex: '10000',
            animation: 'slideInRight 0.3s ease-out',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
            fontSize: '14px',
            fontWeight: '500',
            opacity: '0.95'
        });

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MusicPlayer();
});