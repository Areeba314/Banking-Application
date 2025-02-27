  // Sign Up Form  Validations
  // Real-time validation
const phoneInput = document.getElementById('phone_number');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const phoneError = document.getElementById('phoneError');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');

phoneInput.addEventListener('input', () => {
  if (!/^\d{11}$/.test(phoneInput.value)) {
    phoneError.textContent = "Phone number must be 11 digits.";
  } else {
    phoneError.textContent = "";
  }
});

emailInput.addEventListener('input', () => {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(emailInput.value)) {
    emailError.textContent = "Please enter a valid email address.";
  } else {
    emailError.textContent = "";
  }
});

passwordInput.addEventListener('input', () => {
  if (passwordInput.value.length < 8) {
    passwordError.textContent = "Password must be at least 8 characters long.";
  } else {
    passwordError.textContent = "";
  }
});



// Email validation function
function validateForm() {
  const emailInput = document.getElementById('username');
  const emailError = document.getElementById('emailError');
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(emailInput.value)) {
    emailError.textContent = "Please enter a valid email address.";
    return false; // Prevent form submission
  } else {
    emailError.textContent = ""; // Clear error message
    return true;
  }
}
