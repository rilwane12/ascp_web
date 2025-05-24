// Main JavaScript for Asclepios Prescription Web

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable popovers
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
        // Get the medicaments data from the window object (populated in the template)
        const medicaments = window.medicamentsList || [];
        
        // Simple autocomplete (can be replaced with a more robust solution like Typeahead.js)
        medicamentField.addEventListener('input', function() {
            const input = this.value.toLowerCase();
            const datalist = document.getElementById('medicaments-datalist') || 
                             document.createElement('datalist');
            
            if (!document.getElementById('medicaments-datalist')) {
                datalist.id = 'medicaments-datalist';
                document.body.appendChild(datalist);
                this.setAttribute('list', 'medicaments-datalist');
            }
            
            // Clear existing options
            datalist.innerHTML = '';
            
            // Filter and add matching options
            medicaments.filter(med => med.toLowerCase().includes(input))
                      .slice(0, 10)
                      .forEach(med => {
                          const option = document.createElement('option');
                          option.value = med;
                          datalist.appendChild(option);
                      });
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
});