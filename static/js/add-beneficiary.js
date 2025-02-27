
function openBankSelection() {
    // Navigate to the bank selection page
    window.location.href = '/select_bank';
}
document.getElementById('account_holder_name').addEventListener('input', function() {
    localStorage.setItem('account_holder_name', this.value);
});

document.getElementById('account_number').addEventListener('input', function() {
    localStorage.setItem('account_number', this.value);
});

// Retrieve and populate stored values on page load
document.addEventListener('DOMContentLoaded', function () {
    const accountHolderName = localStorage.getItem('account_holder_name');
    const accountNumber = localStorage.getItem('account_number');
    const selectedBank = localStorage.getItem('selectedBank');
  
    if (accountHolderName) {
        document.getElementById('account_holder_name').value = accountHolderName;
    }
    if (accountNumber) {
        document.getElementById('account_number').value = accountNumber;
    }
    if (selectedBank) {
        document.getElementById('bank-name').textContent = selectedBank;
        document.getElementById('bank-name').style.color = '#333';
        document.getElementById('bank_name').value = selectedBank;
        document.getElementById('accountNumber').value = ''; // Clear input field
        document.getElementById('errorMessage').textContent = ''; // Clear errors
    }
});

function validateAccountNumber() {
    const accountNumber = document.getElementById('account_number').value; // Correct ID
    const errorMessage = document.getElementById('errorMessage');
    const selectedBank = localStorage.getItem('selectedBank'); // Get bank name from localStorage

    errorMessage.textContent = ''; // Clear previous errors
    

    // General validation: numbers only
    if (!/^\d+$/.test(accountNumber)) {
        errorMessage.textContent = "Account number must be numeric only.";
        return;
    }

    // Bank-specific validation
    if (selectedBank === 'Meezan' || selectedBank === 'Alfalah' || selectedBank === 'HBL' || selectedBank === 'MCB') {
        if (accountNumber.length < 10 || accountNumber.length > 16) {
            errorMessage.textContent = `${selectedBank} account number must be 10–16 digits.`;
        }
    } else if (selectedBank === 'EasyPaisa' || selectedBank === 'JazzCash') {
        if (!/^03\d{9}$/.test(accountNumber)) {
            errorMessage.textContent = `${selectedBank} account number must be an 11-digit mobile number starting with 03.`;
        }
    } else {
        errorMessage.textContent = "Please select a bank first.";
    }
}


// Clear localStorage on form submission
document.querySelector('form').addEventListener('submit', function () {
    localStorage.removeItem('account_holder_name');
    localStorage.removeItem('account_number');
    localStorage.removeItem('selectedBank');
});
// Prevent form submission if validation fails
function validateForm() {
const isValid = validateAccountNumber();
return isValid; // Return true if valid, false otherwise
}
// Validate account number on page load
document.addEventListener("DOMContentLoaded", function () {
validateAccountNumber();
});



// Clear localStorage on logout
document.querySelector('.logout-button').addEventListener('click', function () {
    localStorage.clear();
});

