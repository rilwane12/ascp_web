// Main JavaScript for Asclepios Prescription Web Application

// API Helper for making authenticated requests
const API = {
    // Get API headers with CSRF token
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        // Add CSRF token for Django
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        return headers;
    },
    
    // Simple wrapper for fetch with standard options
    async request(url, options = {}) {
        const defaultOptions = {
            headers: this.getHeaders(),
            credentials: 'same-origin' // Send cookies for authentication
        };
        
        const response = await fetch(url, {...defaultOptions, ...options});
        
        // Handle 401 Unauthorized (redirect to login)
        if (response.status === 401) {
            window.location.href = '/login/';
            return null;
        }
        
        // Handle other errors
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
            throw new Error(error.detail || 'An unknown error occurred');
        }
        
        // Parse JSON if the response has content
        if (response.status !== 204) {
            return response.json();
        }
        
        return null;
    },
    
    // GET request
    async get(url, params = {}) {
        // Add query parameters if provided
        const queryParams = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                queryParams.append(key, value);
            }
        });
        
        const queryString = queryParams.toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl);
    },
    
    // POST request
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    // PUT request
    async put(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // PATCH request
    async patch(url, data = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    },
    
    // DELETE request
    async delete(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-dismissible:not(.alert-persistent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Initialize autocomplete for medication field
    const medicamentField = document.getElementById('medicament-autocomplete');
    if (medicamentField) {
        // Set up debounce for API calls
        let debounceTimer;
        
        // Create datalist if it doesn't exist
        const datalist = document.getElementById('medicaments-datalist') || 
                         document.createElement('datalist');
        
        if (!document.getElementById('medicaments-datalist')) {
            datalist.id = 'medicaments-datalist';
            document.body.appendChild(datalist);
            medicamentField.setAttribute('list', 'medicaments-datalist');
        }
        
        // Use API autocomplete endpoint
        medicamentField.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Clear existing options
            datalist.innerHTML = '';
            
            // Don't search if query is too short
            if (query.length < 2) return;
            
            // Clear previous timer
            clearTimeout(debounceTimer);
            
            // Set a new timer to avoid too many API calls
            debounceTimer = setTimeout(async () => {
                try {
                    // Use our new API helper
                    const results = await API.get('/api/medicaments/autocomplete/', { q: query });
                    
                    // Clear existing options
                    datalist.innerHTML = '';
                    
                    // Add options from API results
                    results.forEach(med => {
                        const option = document.createElement('option');
                        option.value = med;
                        datalist.appendChild(option);
                    });
                } catch (error) {
                    console.error('Error fetching medication suggestions:', error);
                }
            }, 300); // 300ms debounce
        });
    }

    // Print prescription functionality
    const printButton = document.getElementById('print-prescription');
    if (printButton) {
        printButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }
    
    // Confirm deletion modals
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.')) {
                e.preventDefault();
            }
        });
    });
    
    // Patient search autocomplete
    const patientSearchField = document.getElementById('patient-search');
    if (patientSearchField) {
        // Set up debounce for API calls
        let debounceTimer;
        
        patientSearchField.addEventListener('keyup', function() {
            const query = this.value.trim();
            const resultsContainer = document.getElementById('search-results');
            
            // Clear previous results
            resultsContainer.innerHTML = '';
            
            // Don't search if query is too short
            if (query.length < 2) {
                resultsContainer.innerHTML = '<p class="text-muted text-center p-3">Entrez au moins 2 caractères</p>';
                return;
            }
            
            // Show loading indicator
            resultsContainer.innerHTML = '<p class="text-center p-3"><i class="fas fa-spinner fa-spin"></i> Recherche en cours...</p>';
            
            // Clear previous timer
            clearTimeout(debounceTimer);
            
            // Set a new timer to avoid too many API calls
            debounceTimer = setTimeout(async () => {
                try {
                    // Use our API helper
                    const data = await API.get('/api/patients/', { search: query });
                    const results = data.results || [];
                    
                    // Clear previous results
                    resultsContainer.innerHTML = '';
                    
                    if (results.length === 0) {
                        resultsContainer.innerHTML = '<p class="text-muted text-center p-3">Aucun patient trouvé</p>';
                        return;
                    }
                    
                    // Create result items
                    results.forEach(patient => {
                        const item = document.createElement('a');
                        item.href = `/patients/${patient.id}/`;
                        item.className = 'list-group-item list-group-item-action';
                        
                        // Format the genre
                        const genre = patient.genre === 'M' ? 'Masculin' : 'Féminin';
                        
                        item.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">${patient.nom} ${patient.prenom}</h6>
                                <small>${patient.age} ans (${genre})</small>
                            </div>
                            <p class="mb-1 small">
                                ${patient.contact ? `<i class="fas fa-phone-alt me-1"></i>${patient.contact}` : ''}
                                ${patient.allergies ? `<span class="ms-2 text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Allergies</span>` : ''}
                            </p>
                        `;
                        resultsContainer.appendChild(item);
                    });
                    
                } catch (error) {
                    console.error('Error fetching patients:', error);
                    resultsContainer.innerHTML = '<p class="text-danger text-center p-3">Erreur lors de la recherche. Veuillez réessayer.</p>';
                }
            }, 300); // 300ms debounce
        });
    }
    
    // Quick stats API call for dashboard
    const dashboardStatsContainer = document.getElementById('dashboard-stats');
    if (dashboardStatsContainer) {
        // Fetch summary stats
        Promise.all([
            fetch('/api/patients/').then(response => response.json()),
            fetch('/api/consultations/').then(response => response.json()),
            fetch('/api/prescriptions/').then(response => response.json())
        ])
        .then(([patients, consultations, prescriptions]) => {
            document.getElementById('patient-count').textContent = patients.count || '0';
            document.getElementById('consultation-count').textContent = consultations.count || '0';
            document.getElementById('prescription-count').textContent = prescriptions.count || '0';
        })
        .catch(error => console.error('Error fetching stats:', error));
    }
    
    // Update consultation form with patient data
    const patientSelect = document.getElementById('id_patient');
    if (patientSelect) {
        patientSelect.addEventListener('change', function() {
            const patientId = this.value;
            if (!patientId) return;
            
            fetch(`/api/patients/${patientId}/`)
                .then(response => response.json())
                .then(patient => {
                    // Update form fields or display info about selected patient
                    const patientInfoElement = document.getElementById('patient-info');
                    if (patientInfoElement) {
                        patientInfoElement.innerHTML = `
                            <div class="alert alert-info">
                                <h6>${patient.nom} ${patient.prenom}</h6>
                                <p>${patient.age} ans - ${patient.genre === 'M' ? 'Masculin' : 'Féminin'}</p>
                                <p>${patient.contact || 'Pas de contact'}</p>
                            </div>
                        `;
                        patientInfoElement.style.display = 'block';
                    }
                })
                .catch(error => console.error('Error fetching patient details:', error));
        });
    }
});