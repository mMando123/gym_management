// التهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initializeDataTables();
    initializeFlatpickr();
    initializeSidebarToggle();
    initializeImagePreview();
});

// ========== Sidebar Toggle ==========
function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
}

// ========== DataTables Initialization ==========
function initializeDataTables() {
    if ($.fn.dataTable) {
        $('.data-table').not('.initialized').each(function() {
            $(this).addClass('initialized');
            $(this).DataTable({
                language: {
                    "sProcessing": "جاري المعالجة...",
                    "sLengthMenu": "اعرض _MENU_ عنصر",
                    "sZeroRecords": "لم يتم العثور على عناصر",
                    "sInfo": "عرض _START_ إلى _END_ من _TOTAL_ عنصر",
                    "sInfoEmpty": "عرض 0 إلى 0 من 0 عنصر",
                    "sInfoFiltered": "(مصفى من _MAX_ عنصر كلي)",
                    "sInfoPostFix": "",
                    "sSearch": "ابحث:",
                    "sUrl": "",
                    "oPaginate": {
                        "sFirst": "الأول",
                        "sPrevious": "السابق",
                        "sNext": "التالي",
                        "sLast": "الأخير"
                    }
                },
                pageLength: 10,
                ordering: true,
                searching: true
            });
        });
    }
}

// ========== Flatpickr Date Picker ==========
function initializeFlatpickr() {
    flatpickr.localize(flatpickr.l10ns.ar);
    
    const dateInputs = document.querySelectorAll('.date-picker');
    dateInputs.forEach(input => {
        flatpickr(input, {
            dateFormat: "Y-m-d",
            locale: "ar"
        });
    });
}

// ========== Image Preview ==========
function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById(input.dataset.previewId);
                    if (preview) {
                        preview.src = event.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// ========== Delete Confirmation ==========
function deleteConfirmation(url, itemName = 'العنصر') {
    Swal.fire({
        title: 'هل أنت متأكد؟',
        text: `هل تريد حقاً حذف ${itemName}؟ لا يمكن التراجع عن هذا الإجراء.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#EF4444',
        cancelButtonColor: '#6B7280',
        confirmButtonText: 'نعم، احذفه!',
        cancelButtonText: 'إلغاء'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = url;
        }
    });
}

// ========== Success Toast Message ==========
function showSuccessMessage(message = 'تم العملية بنجاح') {
    Swal.fire({
        icon: 'success',
        title: 'نجح!',
        text: message,
        confirmButtonColor: '#4F46E5',
        timer: 3000,
        timerProgressBar: true
    });
}

// ========== Error Toast Message ==========
function showErrorMessage(message = 'حدث خطأ ما') {
    Swal.fire({
        icon: 'error',
        title: 'خطأ!',
        text: message,
        confirmButtonColor: '#EF4444'
    });
}

// ========== Warning Message ==========
function showWarningMessage(message = 'تحذير') {
    Swal.fire({
        icon: 'warning',
        title: 'تحذير',
        text: message,
        confirmButtonColor: '#F59E0B'
    });
}

// ========== Print Function ==========
function printElement(elementId) {
    const printContents = document.getElementById(elementId).innerHTML;
    const originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}

// ========== Export to Excel ==========
function exportToExcel(tableId, fileName) {
    const table = document.getElementById(tableId);
    const csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => {
            csvRow.push(col.innerText);
        });
        csv.push(csvRow.join(','));
    });
    
    const csvContent = 'data:text/csv;charset=utf-8,%EF%BB%BF' + csv.join('\n');
    const link = document.createElement('a');
    link.setAttribute('href', encodeURI(csvContent));
    link.setAttribute('download', fileName + '.csv');
    link.click();
}

// ========== AJAX Helper ==========
function ajaxRequest(url, method = 'GET', data = null) {
    return fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: data ? JSON.stringify(data) : null
    }).then(response => response.json());
}

// ========== Get CSRF Token ==========
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== Quick Search ==========
function quickSearch(query, searchType = 'members') {
    if (!query || query.length < 2) {
        return;
    }
    
    ajaxRequest(`/api/search/?q=${query}&type=${searchType}`)
        .then(data => {
            updateSearchResults(data, searchType);
        })
        .catch(error => console.error('Search error:', error));
}

function updateSearchResults(data, searchType) {
    // يمكن تخصيص هذه الدالة حسب احتياجات التطبيق
    console.log('Search results:', data);
}

// ========== Chart Initialization ==========
function initializeChart(canvasId, chartType, labels, data, label) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const colors = {
        primary: '#4F46E5',
        secondary: '#0EA5E9',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444'
    };
    
    return new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: colors.primary,
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: chartType === 'line'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        font: {
                            family: "'Cairo', sans-serif"
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ========== Form Validation ==========
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// ========== Calculate End Date ==========
function calculateEndDate(startDate, duration) {
    const start = new Date(startDate);
    const end = new Date(start.getTime() + duration * 24 * 60 * 60 * 1000);
    return end.toISOString().split('T')[0];
}

// ========== Format Currency ==========
function formatCurrency(value) {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(value);
}

// ========== Format Date ==========
function formatDate(date) {
    return new Intl.DateTimeFormat('ar-SA').format(new Date(date));
}

// ========== Disable Form Button During Submit ==========
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>جاري المعالجة...';
        }
    });
});

// ========== Close Alert Messages Auto ==========
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
});

// ========== CSRF Token Helper ==========
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// ========== Quick Search AJAX ==========
const quickSearchInput = document.getElementById('quickSearch');
if (quickSearchInput) {
    quickSearchInput.addEventListener('keyup', function() {
        const query = this.value.trim();
        const resultsContainer = document.getElementById('searchResults');
        const resultsList = document.getElementById('searchResultsList');
        
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }
        
        fetch(`/members/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultsList.innerHTML = data.results.map(member => `
                        <a href="${member.url}" class="list-group-item list-group-item-action">
                            <i class="fas fa-user"></i> <strong>${member.name}</strong>
                            <br><small class="text-muted">${member.phone}</small>
                        </a>
                    `).join('');
                    resultsContainer.style.display = 'block';
                } else {
                    resultsList.innerHTML = '<div class="p-3 text-muted text-center">لا توجد نتائج</div>';
                    resultsContainer.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('خطأ:', error);
                resultsContainer.style.display = 'none';
            });
    });
}

// ========== Delete Confirmation ==========
function confirmDelete(message = 'هل أنت متأكد؟') {
    return confirm(message);
}

// ========== SweetAlert Delete ==========
function confirmDeleteSweetAlert(url, title = 'حذف العنصر') {
    Swal.fire({
        title: title,
        text: 'لن تتمكن من استرجاع هذا العنصر!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'نعم، احذف!',
        cancelButtonText: 'إلغاء'
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = url;
        }
    });
}

// ========== Member Quick Info AJAX ==========
function getMemberInfo(memberId) {
    return fetch(`/members/api/${memberId}/info/`)
        .then(response => response.json());
}

// ========== Show Member in Modal ==========
function showMemberModal(memberId) {
    getMemberInfo(memberId).then(data => {
        const modal = new bootstrap.Modal(document.getElementById('memberModal'));
        document.getElementById('memberName').textContent = data.name;
        document.getElementById('memberPhone').textContent = data.phone;
        document.getElementById('memberAge').textContent = data.age;
        document.getElementById('memberSubscription').textContent = data.has_active_subscription ? 'نشط' : 'بلا اشتراك';
        modal.show();
    });
}

// ========== Format Currency ==========
function formatCurrency(amount) {
    return new Intl.NumberFormat('ar-SA', {
        style: 'currency',
        currency: 'SAR'
    }).format(amount);
}

// ========== AJAX Setup with CSRF ==========
if (typeof jQuery !== 'undefined') {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}
