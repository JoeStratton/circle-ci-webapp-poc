/**
 * CircleCI Demo App JavaScript
 * 
 * This module handles:
 * - Dark mode toggle with persistence
 * - API interactions for user management
 * - Database testing functionality
 * - Dynamic UI updates
 */

// Dark Mode Management
class DarkModeManager {
    constructor() {
        this.toggle = document.getElementById('darkModeToggle');
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Set initial theme
        this.setTheme(this.theme);
        
        // Set toggle state
        this.toggle.checked = this.theme === 'dark';
        
        // Add event listener
        this.toggle.addEventListener('change', (e) => {
            this.setTheme(e.target.checked ? 'dark' : 'light');
        });
    }

    setTheme(theme) {
        this.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
}

// API Client for backend communication
class APIClient {
    constructor() {
        this.baseURL = '/api';
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }

    async getUsers() {
        return this.request('/users');
    }

    async createUser(userData) {
        return this.request('/users', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    async deleteUser(userId) {
        return this.request(`/users/${userId}`, {
            method: 'DELETE'
        });
    }

    async testHealth() {
        return this.request('/health');
    }
}

// UI Manager for dynamic content updates
class UIManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.dbResult = document.getElementById('dbResult');
        this.userResult = document.getElementById('userResult');
        this.userList = document.getElementById('userList');
    }

    showMessage(container, message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `card ${type}`;
        messageDiv.innerHTML = `<p>${message}</p>`;
        container.innerHTML = '';
        container.appendChild(messageDiv);
    }

    showLoading(container) {
        container.innerHTML = '<div class="card loading">Loading...</div>';
    }

    async loadUsers() {
        try {
            this.showLoading(this.userList);
            const users = await this.apiClient.getUsers();
            
            if (Array.isArray(users) && users.length > 0) {
                const userHTML = users.map(user => `
                    <div class="user-item">
                        <strong>${this.escapeHtml(user.username)}</strong>
                        <span class="user-email">(${this.escapeHtml(user.email)})</span>
                        <span class="user-date">${new Date(user.created_at).toLocaleString()}</span>
                    </div>
                `).join('');
                this.userList.innerHTML = userHTML;
            } else {
                this.userList.innerHTML = '<div class="user-item">No users found</div>';
            }
        } catch (error) {
            console.error('Error loading users:', error);
            this.userList.innerHTML = '<div class="user-item error">Error loading users</div>';
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Main Application Class
class App {
    constructor() {
        this.darkMode = new DarkModeManager();
        this.apiClient = new APIClient();
        this.ui = new UIManager(this.apiClient);
        this.init();
    }

    init() {
        // Load initial data
        this.ui.loadUsers();
        
        // Bind event handlers
        this.bindEvents();
    }

    bindEvents() {
        // Database test button
        window.testDatabase = () => this.testDatabase();
        
        // Create test user button
        window.createUser = () => this.createTestUser();
        
        // Add user button
        window.addUser = () => this.addUser();
    }

    async testDatabase() {
        try {
            this.ui.showLoading(this.ui.dbResult);
            const data = await this.apiClient.testHealth();
            this.ui.showMessage(
                this.ui.dbResult, 
                `Database test successful: ${JSON.stringify(data, null, 2)}`, 
                'success'
            );
        } catch (error) {
            this.ui.showMessage(
                this.ui.dbResult, 
                `Error: ${error.message}`, 
                'error'
            );
        }
    }

    async createTestUser() {
        const testUser = {
            username: `testuser_${Date.now()}`,
            email: `test_${Date.now()}@example.com`
        };

        try {
            this.ui.showLoading(this.ui.dbResult);
            const data = await this.apiClient.createUser(testUser);
            this.ui.showMessage(
                this.ui.dbResult, 
                `User created: ${JSON.stringify(data, null, 2)}`, 
                'success'
            );
            this.ui.loadUsers();
        } catch (error) {
            this.ui.showMessage(
                this.ui.dbResult, 
                `Error: ${error.message}`, 
                'error'
            );
        }
    }

    async addUser() {
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();

        if (!username || !email) {
            alert('Please enter both username and email');
            return;
        }

        // Basic email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address');
            return;
        }

        try {
            this.ui.showLoading(this.ui.userResult);
            const data = await this.apiClient.createUser({ username, email });
            this.ui.showMessage(
                this.ui.userResult, 
                `User added: ${JSON.stringify(data, null, 2)}`, 
                'success'
            );
            
            // Clear form
            document.getElementById('username').value = '';
            document.getElementById('email').value = '';
            
            // Reload users
            this.ui.loadUsers();
        } catch (error) {
            this.ui.showMessage(
                this.ui.userResult, 
                `Error: ${error.message}`, 
                'error'
            );
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
