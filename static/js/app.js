// Voucher System Frontend JavaScript
class VoucherApp {
        constructor() {
            this.apiBase = '/api';
            this.token = localStorage.getItem('auth_token');
            this.user = JSON.parse(localStorage.getItem('user') || '{}');
            this.currentTab = 'active'; // Track current tab
            this.currentPage = 1; // Track current page
            this.itemsPerPage = 5; // Items per page
            this.totalItems = 0; // Total items count
            this.init();
        }

    init() {
        this.setupEventListeners();
        this.checkAuth();
    }

    setupEventListeners() {
        // Login form
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Bulk voucher creation form
        const bulkVoucherForm = document.getElementById('bulkVoucherForm');
        if (bulkVoucherForm) {
            bulkVoucherForm.addEventListener('submit', (e) => this.handleBulkVoucherCreate(e));
        }

            // Check balance form
            const checkBalanceForm = document.getElementById('checkBalanceForm');
            if (checkBalanceForm) {
                checkBalanceForm.addEventListener('submit', (e) => this.handleCheckBalance(e));
            }

            // Recharge form
            const rechargeForm = document.getElementById('rechargeForm');
            if (rechargeForm) {
                rechargeForm.addEventListener('submit', (e) => this.handleRecharge(e));
            }


        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

            // Auto-uppercase voucher code inputs
            const rechargeVoucherCodeInput = document.getElementById('recharge_voucher_code');
            if (rechargeVoucherCodeInput) {
                rechargeVoucherCodeInput.addEventListener('input', (e) => {
                    e.target.value = e.target.value.toUpperCase();
                });
            }

            const balanceVoucherCodeInput = document.getElementById('balance_voucher_code');
            if (balanceVoucherCodeInput) {
                balanceVoucherCodeInput.addEventListener('input', (e) => {
                    e.target.value = e.target.value.toUpperCase();
                });
            }

            // Modal close buttons
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal')) {
                    this.closeModal();
                }
            });

            // Close dropdowns when clicking outside
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.dropdown')) {
                    document.querySelectorAll('.dropdown-menu').forEach(menu => {
                        menu.style.display = 'none';
                    });
                }
            });
    }

    checkAuth() {
        if (!this.token) {
            this.showLogin();
            return;
        }
        this.showDashboard();
        this.loadVouchers();
    }

    async handleLogin(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const credentials = {
            username: formData.get('username'),
            password: formData.get('password')
        };

        try {
            const response = await this.apiCall('/get-token/', 'POST', credentials);
            this.token = response.token;
            this.user = response;
            localStorage.setItem('auth_token', this.token);
            localStorage.setItem('user', JSON.stringify(this.user));
            this.showSuccess('Login successful!');
            this.showDashboard();
            this.loadVouchers();
        } catch (error) {
            this.showError('Login failed: ' + error.message);
        }
    }

    async handleBulkVoucherCreate(e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const amount = parseFloat(formData.get('amount'));
        const count = parseInt(formData.get('count'));

        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.innerHTML = '<span class="loading"></span> Creating...';
        submitBtn.disabled = true;

        try {
            let successCount = 0;
            let errorCount = 0;

            for (let i = 0; i < count; i++) {
                try {
                    await this.apiCall('/vouchers/', 'POST', { initial_value: amount });
                    successCount++;
                } catch (error) {
                    errorCount++;
                    console.error(`Failed to create voucher ${i + 1}:`, error);
                }
            }

            if (successCount > 0) {
                this.showSuccess(`Successfully created ${successCount} vouchers worth Rs ${amount} each!`);
                this.loadVouchers();
            }
            
            if (errorCount > 0) {
                this.showError(`Failed to create ${errorCount} vouchers. Check console for details.`);
            }

            e.target.reset();
        } catch (error) {
            this.showError('Failed to create vouchers: ' + error.message);
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

        async handleCheckBalance(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const voucherCode = formData.get('voucher_code');

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<span class="loading"></span> Checking...';
            submitBtn.disabled = true;

            try {
                // Get voucher details to check balance
                const vouchers = await this.apiCall('/vouchers/', 'GET');
                const voucher = vouchers.results?.find(v => v.code === voucherCode) || 
                              vouchers.find(v => v.code === voucherCode);
                
                if (voucher) {
                    const balanceResult = document.getElementById('balance_result');
                    if (balanceResult) {
                        balanceResult.value = `Rs ${voucher.current_balance}`;
                        balanceResult.style.color = voucher.current_balance > 0 ? 'var(--success-color)' : 'var(--text-secondary)';
                    }
                    this.showSuccess(`Voucher ${voucherCode} balance: Rs ${voucher.current_balance}`);
                } else {
                    // Check if voucher exists but is disabled or sold
                    const disabledVouchers = await this.apiCall('/vouchers/disabled/', 'GET');
                    const soldVouchers = await this.apiCall('/vouchers/sold/', 'GET');
                    
                    const disabledVoucher = disabledVouchers.find(v => v.code === voucherCode);
                    const soldVoucher = soldVouchers.find(v => v.code === voucherCode);
                    
                    if (disabledVoucher) {
                        const balanceResult = document.getElementById('balance_result');
                        if (balanceResult) {
                            balanceResult.value = `Rs ${disabledVoucher.current_balance} (DISABLED)`;
                            balanceResult.style.color = 'var(--danger-color)';
                        }
                        this.showError(`Voucher ${voucherCode} is disabled. Balance: Rs ${disabledVoucher.current_balance}`);
                    } else if (soldVoucher) {
                        const balanceResult = document.getElementById('balance_result');
                        if (balanceResult) {
                            balanceResult.value = `Rs ${soldVoucher.current_balance} (SOLD)`;
                            balanceResult.style.color = 'var(--warning-color)';
                        }
                        this.showError(`Voucher ${voucherCode} has been sold. Balance: Rs ${soldVoucher.current_balance}`);
                    } else {
                        const balanceResult = document.getElementById('balance_result');
                        if (balanceResult) {
                            balanceResult.value = 'Voucher not found';
                            balanceResult.style.color = 'var(--danger-color)';
                        }
                        this.showError(`Voucher ${voucherCode} not found`);
                    }
                }
            } catch (error) {
                const balanceResult = document.getElementById('balance_result');
                if (balanceResult) {
                    balanceResult.value = 'Error checking balance';
                    balanceResult.style.color = 'var(--danger-color)';
                }
                this.showError('Failed to check voucher balance: ' + error.message);
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }

        async handleRecharge(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const voucherCode = formData.get('voucher_code');
            const amount = parseInt(formData.get('amount'));

            try {
                await this.apiCall(`/vouchers/${voucherCode}/recharge/`, 'POST', { amount });
                this.showSuccess(`Voucher recharged with Rs ${amount}!`);
                this.loadVouchers(); // This will update stats too
                e.target.reset();
            } catch (error) {
                this.showError('Failed to recharge voucher: ' + error.message);
            }
        }


        async loadVouchers() {
            try {
                let endpoint;
                if (this.currentTab === 'active') {
                    endpoint = '/vouchers/';
                } else if (this.currentTab === 'disabled') {
                    endpoint = '/vouchers/disabled/';
                } else if (this.currentTab === 'sold') {
                    endpoint = '/vouchers/sold/';
                }
                
                console.log('Loading vouchers from endpoint:', endpoint, 'for tab:', this.currentTab);
                const response = await this.apiCall(endpoint, 'GET');
                console.log('Received vouchers:', response);
                
                // Handle both paginated and non-paginated responses
                const vouchers = response.results || response;
                this.totalItems = response.count || vouchers.length;
                
                // Apply client-side pagination
                const startIndex = (this.currentPage - 1) * this.itemsPerPage;
                const endIndex = startIndex + this.itemsPerPage;
                const paginatedVouchers = vouchers.slice(startIndex, endIndex);
                
                this.displayVouchers(paginatedVouchers);
                this.updatePagination();
                await this.loadStatistics();
            } catch (error) {
                this.showError('Failed to load vouchers: ' + error.message);
            }
        }

        switchTab(tab) {
            this.currentTab = tab;
            this.currentPage = 1; // Reset to first page when switching tabs
            
            // Update tab buttons
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            if (tab === 'active') {
                document.getElementById('activeTab').classList.add('active');
            } else if (tab === 'disabled') {
                document.getElementById('disabledTab').classList.add('active');
            } else if (tab === 'sold') {
                document.getElementById('soldTab').classList.add('active');
            }
            
            // Load appropriate vouchers
            this.loadVouchers();
        }

    async loadStatistics() {
        try {
            const stats = await this.apiCall('/statistics/', 'GET');
            this.updateStatsFromAPI(stats);
        } catch (error) {
            console.error('Failed to load statistics:', error);
        }
    }

    displayVouchers(vouchers) {
        const container = document.getElementById('vouchersContainer');
        if (!container) return;

        console.log('Displaying vouchers:', vouchers.length, 'for tab:', this.currentTab);

        if (vouchers.length === 0) {
            let message;
            if (this.currentTab === 'active') {
                message = 'No active vouchers found';
            } else if (this.currentTab === 'disabled') {
                message = 'No disabled vouchers found';
            } else if (this.currentTab === 'sold') {
                message = 'No sold vouchers found';
            }
            container.innerHTML = `<div class="text-center text-secondary">${message}</div>`;
            return;
        }

        const vouchersHTML = `
            <table class="voucher-table">
                <thead>
                    <tr>
                        <th>Voucher Code</th>
                        <th>Remaining Balance</th>
                        <th>Total Loaded</th>
                        <th>Spent</th>
                        <th>Created</th>
                        <th>Creator</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${vouchers.map(voucher => `
                        <tr>
                            <td class="voucher-code-cell">
                                <span class="voucher-code">${voucher.code}</span>
                            </td>
                            <td class="balance-cell">
                                <span class="balance-amount">Rs ${voucher.current_balance}</span>
                            </td>
                            <td class="total-loaded-cell">
                                <span class="total-loaded">Rs ${voucher.total_loaded > 0 ? voucher.total_loaded : voucher.current_balance}</span>
                            </td>
                            <td class="spent-cell">
                                <span class="spent-amount">Rs ${Math.max(0, (voucher.total_loaded > 0 ? voucher.total_loaded : voucher.current_balance) - voucher.current_balance)}</span>
                            </td>
                            <td class="created-cell">
                                <span class="created-date">${new Date(voucher.created_at).toLocaleDateString()}</span>
                            </td>
                            <td class="creator-cell">
                                <span class="creator-name">${voucher.creator ? voucher.creator.username : 'Unknown'}</span>
                            </td>
                            <td class="actions-cell">
                                <div class="voucher-actions">
                                    ${this.currentTab === 'active' ? `
                                        <button onclick="app.copyAndMarkSold(${voucher.id}, '${voucher.code}')" class="btn btn-success btn-sm">
                                            Copy & Mark Sold
                                        </button>
                                        <div class="dropdown">
                                            <button class="btn btn-outline btn-sm dropdown-toggle" onclick="app.toggleDropdown(${voucher.id})">
                                                ⋯
                                            </button>
                                            <div class="dropdown-menu" id="dropdown-${voucher.id}" style="display: none;">
                                                <button onclick="app.viewVoucherDetails(${voucher.id})" class="dropdown-item">
                                                    Details
                                                </button>
                                                <button onclick="app.disableVoucher(${voucher.id})" class="dropdown-item">
                                                    Disable
                                                </button>
                                            </div>
                                        </div>
                                    ` : this.currentTab === 'disabled' ? `
                                        <div class="dropdown">
                                            <button class="btn btn-outline btn-sm dropdown-toggle" onclick="app.toggleDropdown(${voucher.id})">
                                                ⋯
                                            </button>
                                            <div class="dropdown-menu" id="dropdown-${voucher.id}" style="display: none;">
                                                <button onclick="app.viewVoucherDetails(${voucher.id})" class="dropdown-item">
                                                    Details
                                                </button>
                                                <button onclick="app.enableVoucher(${voucher.id})" class="dropdown-item">
                                                    Enable
                                                </button>
                                            </div>
                                        </div>
                                    ` : `
                                        <div class="dropdown">
                                            <button class="btn btn-outline btn-sm dropdown-toggle" onclick="app.toggleDropdown(${voucher.id})">
                                                ⋯
                                            </button>
                                            <div class="dropdown-menu" id="dropdown-${voucher.id}" style="display: none;">
                                                <button onclick="app.viewVoucherDetails(${voucher.id})" class="dropdown-item">
                                                    Details
                                                </button>
                                            </div>
                                        </div>
                                    `}
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = vouchersHTML;
    }

    updateStatsFromAPI(stats) {
        // Update the display with API statistics
        const totalVouchersEl = document.getElementById('totalVouchers');
        const totalBalanceEl = document.getElementById('totalBalance');
        const activeVouchersEl = document.getElementById('activeVouchers');
        const disabledVouchersEl = document.getElementById('disabledVouchers');
        const soldVouchersEl = document.getElementById('soldVouchers');

        if (totalVouchersEl) {
            totalVouchersEl.textContent = stats.total_vouchers;
        }
        if (totalBalanceEl) {
            totalBalanceEl.textContent = `Rs ${stats.total_balance.toFixed(2)}`;
        }
        if (activeVouchersEl) {
            activeVouchersEl.textContent = stats.active_vouchers;
        }
        if (disabledVouchersEl) {
            disabledVouchersEl.textContent = stats.disabled_vouchers;
        }
        if (soldVouchersEl) {
            soldVouchersEl.textContent = stats.sold_vouchers;
        }
    }

    fillRechargeForm(code) {
        // Fill the recharge form on the dashboard
        const voucherCodeInput = document.getElementById('recharge_voucher_code');
        if (voucherCodeInput) {
            voucherCodeInput.value = code;
            voucherCodeInput.focus();
        }
        
        // Scroll to the recharge section
        const rechargeSection = document.querySelector('#rechargeForm').closest('.card');
        if (rechargeSection) {
            rechargeSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    viewVoucherDetails(id) {
        // Implementation for viewing voucher details
        this.showInfo('Voucher details feature coming soon!');
    }

    async disableVoucher(id) {
        if (confirm('Are you sure you want to disable this voucher? Disabled vouchers cannot be used for payments but can be re-enabled later.')) {
            try {
                const response = await this.apiCall(`/vouchers/${id}/`, 'DELETE');
                this.showSuccess(response.message || 'Voucher disabled successfully!');
                this.loadVouchers(); // This will update stats too
            } catch (error) {
                console.error('Disable voucher error:', error);
                this.showError('Failed to disable voucher: ' + error.message);
            }
        }
    }

    async enableVoucher(id) {
        if (confirm('Are you sure you want to enable this voucher? It will be available for payments again.')) {
            try {
                // For now, we'll use a PATCH request to enable the voucher
                const response = await this.apiCall(`/vouchers/${id}/enable/`, 'POST');
                this.showSuccess(response.message || 'Voucher enabled successfully!');
                this.loadVouchers(); // This will update stats too
            } catch (error) {
                console.error('Enable voucher error:', error);
                this.showError('Failed to enable voucher: ' + error.message);
            }
        }
    }

    async copyAndMarkSold(id, code) {
        try {
            // Copy voucher code to clipboard
            await navigator.clipboard.writeText(code);
            
            // Mark voucher as sold
            const response = await this.apiCall(`/vouchers/${id}/mark-sold/`, 'POST');
            this.showSuccess(`Voucher code ${code} copied to clipboard and marked as sold!`);
            this.loadVouchers(); // This will update stats too
        } catch (error) {
            console.error('Copy and mark sold error:', error);
            this.showError('Failed to copy and mark voucher as sold: ' + error.message);
        }
    }

        toggleDropdown(id) {
            // Close all other dropdowns first
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                if (menu.id !== `dropdown-${id}`) {
                    menu.style.display = 'none';
                }
            });
            
            // Toggle the current dropdown
            const dropdown = document.getElementById(`dropdown-${id}`);
            if (dropdown) {
                dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
            }
        }

        updatePagination() {
            const paginationContainer = document.getElementById('paginationContainer');
            const paginationInfo = document.getElementById('paginationInfo');
            const prevButton = document.getElementById('prevPage');
            const nextButton = document.getElementById('nextPage');
            const pageNumbers = document.getElementById('pageNumbers');

            if (!paginationContainer || this.totalItems <= this.itemsPerPage) {
                if (paginationContainer) {
                    paginationContainer.style.display = 'none';
                }
                return;
            }

            paginationContainer.style.display = 'flex';

            // Update pagination info
            const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
            const endItem = Math.min(this.currentPage * this.itemsPerPage, this.totalItems);
            paginationInfo.textContent = `Showing ${startItem}-${endItem} of ${this.totalItems} vouchers`;

            // Update prev/next buttons
            prevButton.disabled = this.currentPage === 1;
            nextButton.disabled = this.currentPage >= Math.ceil(this.totalItems / this.itemsPerPage);

            // Generate page numbers
            const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
            let pageNumbersHTML = '';

            // Show up to 5 page numbers
            const startPage = Math.max(1, this.currentPage - 2);
            const endPage = Math.min(totalPages, startPage + 4);

            for (let i = startPage; i <= endPage; i++) {
                const isActive = i === this.currentPage ? 'active' : '';
                pageNumbersHTML += `<button class="page-number ${isActive}" onclick="app.goToPage(${i})">${i}</button>`;
            }

            pageNumbers.innerHTML = pageNumbersHTML;
        }

        goToPage(page) {
            this.currentPage = page;
            this.loadVouchers();
        }

        previousPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadVouchers();
            }
        }

        nextPage() {
            const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
            if (this.currentPage < totalPages) {
                this.currentPage++;
                this.loadVouchers();
            }
        }

    showLogin() {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('dashboard').style.display = 'none';
    }

    showDashboard() {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
    }




    closeModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    logout() {
        this.token = null;
        this.user = {};
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        this.showLogin();
    }

    async apiCall(endpoint, method = 'GET', data = null) {
        const url = this.apiBase + endpoint;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            options.headers['Authorization'] = `Token ${this.token}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorData.error || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || errorMessage;
            }
            throw new Error(errorMessage);
        }

        // Handle empty responses
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            return { message: 'Operation completed successfully' };
        }

        try {
            return await response.json();
        } catch (e) {
            // If JSON parsing fails, return a success message
            return { message: 'Operation completed successfully' };
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'error');
    }

    showInfo(message) {
        this.showAlert(message, 'warning');
    }

    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        alertContainer.appendChild(alert);
        
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new VoucherApp();
});
